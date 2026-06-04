from __future__ import annotations

import json
import os
import secrets
from datetime import date
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request

from lab_memory_atlas.auth import hash_password, verify_password
from lab_memory_atlas.models import ActionStatus, MeetingType, ReviewStatus
from lab_memory_atlas.pipeline import export_state_snapshot, import_transcript
from lab_memory_atlas.storage import (
    DEFAULT_DATA_DIR,
    add_member_to_project,
    apply_review_decision,
    action_viewer_ids,
    can_view_action,
    list_from_text,
    load_state,
    refresh_helpers,
    refresh_project_people,
    remove_member_from_project,
    save_state,
    set_archived,
    unique_extend,
    upsert_person,
    upsert_project,
)


ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

DATA_DIR = Path(os.getenv("LAB_ATLAS_DATA_DIR", str(DEFAULT_DATA_DIR)))

app = FastAPI(title="Lab Memory Atlas", version="0.1.0")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("LAB_ATLAS_SESSION_SECRET") or secrets.token_urlsafe(32),
    same_site="lax",
    https_only=False,
)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
templates = Jinja2Templates(directory=str(ROOT / "templates"))


def get_state():
    return load_state(DATA_DIR)


def persist(state) -> None:
    save_state(state, DATA_DIR)


def is_admin(request: Request) -> bool:
    return bool(request.session.get("admin_authenticated"))


def session_person_id(request: Request) -> str | None:
    value = request.session.get("person_id")
    return str(value) if value else None


def current_person(request: Request):
    person_id = session_person_id(request)
    if not person_id:
        return None
    state = get_state()
    person = state.people.get(person_id)
    if person is None or person.archived:
        request.session.pop("person_id", None)
        return None
    return person


def admin_password() -> str | None:
    value = os.getenv("LAB_ATLAS_ADMIN_PASSWORD", "").strip()
    return value or None


def require_admin(request: Request):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    return None


def require_member_or_admin(request: Request):
    if is_admin(request) or current_person(request):
        return None
    return RedirectResponse(url="/login", status_code=303)


def render(request: Request, name: str, context: dict):
    person = current_person(request)
    context = {
        "request": request,
        "admin_logged_in": is_admin(request),
        "current_person": person,
        "member_logged_in": person is not None,
        **context,
    }
    return templates.TemplateResponse(request, name, context)


def ui_state(state, viewer_id: str | None = None, *, admin: bool = False, include_reviews: bool = False) -> dict:
    people = []
    visible_people = {person_id: person for person_id, person in state.people.items() if not person.archived}
    visible_projects = {project_id: project for project_id, project in state.projects.items() if not project.archived}
    global_supervisors = [person for person in visible_people.values() if person.is_global_supervisor]
    for person in sorted(visible_people.values(), key=lambda item: (item.role, item.name)):
        approved_actions = [
            state.actions[action_id]
            for action_id in person.action_ids
            if (
                action_id in state.actions
                and not state.actions[action_id].archived
                and state.actions[action_id].review_status == ReviewStatus.APPROVED
                and can_view_action(state, action_id, viewer_id, admin=admin)
            )
        ]
        helpers = [state.people[helper_id].name for helper_id in person.helper_ids if helper_id in visible_people]
        supervisors = [state.people[supervisor_id].name for supervisor_id in person.supervisor_ids if supervisor_id in visible_people]
        pi_supervisors = [supervisor.name for supervisor in global_supervisors if supervisor.id != person.id]
        supervisees = [
            other.name
            for other in visible_people.values()
            if person.id in other.supervisor_ids
        ]
        action_records = []
        for action in approved_actions:
            record = action.model_dump(mode="json")
            record["owner_name"] = state.people[action.owner_id].name if action.owner_id in state.people else "Unassigned"
            action_records.append(record)
        people.append(
            {
                "id": person.id,
                "name": person.name,
                "role": person.role,
                "intro": person.intro,
                "topics": person.topics,
                "methods": person.methods,
                "projects": [pid for pid in person.projects if pid in visible_projects],
                "project_labels": [state.projects[pid].label for pid in person.projects if pid in visible_projects],
                "challenges": person.challenges,
                "recent_updates": person.recent_updates,
                "helpers": helpers,
                "supervisors": supervisors,
                "pi_supervisors": pi_supervisors,
                "supervisees": supervisees,
                "is_global_supervisor": person.is_global_supervisor,
                "action_count": len([action for action in approved_actions if action.status not in {ActionStatus.DONE}]),
                "actions": action_records,
                "last_seen_meeting_id": person.last_seen_meeting_id,
            }
        )

    projects = []
    for project in sorted(visible_projects.values(), key=lambda item: (item.kind != "sig", item.label)):
        projects.append(
            {
                "id": project.id,
                "label": project.label,
                "kind": project.kind,
                "description": project.description,
                "keywords": project.keywords,
                "people": [state.people[pid].name for pid in project.person_ids if pid in visible_people],
                "person_ids": [pid for pid in project.person_ids if pid in visible_people],
                "open_challenges": project.open_challenges,
            }
        )

    pending_reviews = [
        item.model_dump(mode="json")
        for item in sorted(state.review_items.values(), key=lambda item: item.created_at, reverse=True)
        if (admin or include_reviews) and item.status == ReviewStatus.PENDING and not item.archived
    ]
    meetings = [
        meeting.model_dump(mode="json")
        for meeting in sorted(state.meetings.values(), key=lambda item: item.imported_at, reverse=True)
        if not meeting.archived
    ]
    actions = []
    for action in sorted(state.actions.values(), key=lambda item: (-item.priority_score, item.title)):
        if action.review_status != ReviewStatus.APPROVED or action.archived:
            continue
        if not can_view_action(state, action.id, viewer_id, admin=admin):
            continue
        record = action.model_dump(mode="json")
        record["owner_name"] = state.people[action.owner_id].name if action.owner_id in state.people else "Unassigned"
        actions.append(record)
    followups = [
        question.model_dump(mode="json")
        for question in sorted(state.literature_questions.values(), key=lambda item: (-item.priority_score, item.question))
        if question.review_status == ReviewStatus.APPROVED and not question.archived
    ]
    return {
        "people": people,
        "projects": projects,
        "pending_reviews": pending_reviews,
        "meetings": meetings,
        "actions": actions,
        "followups": followups,
        "counts": {
            "people": len(people),
            "projects": len(projects),
            "meetings": len(meetings),
            "pending_reviews": len(pending_reviews),
            "open_actions": len([action for action in actions if action["status"] not in {"done"}]),
            "followups": len(followups),
        },
    }


def _action_record(state, action) -> dict:
    record = action.model_dump(mode="json")
    record["owner_name"] = state.people[action.owner_id].name if action.owner_id in state.people else "Unassigned"
    return record


def project_detail_state(state, project_id: str, viewer_id: str | None = None, *, admin: bool = False) -> dict:
    if project_id not in state.projects or state.projects[project_id].archived:
        raise HTTPException(status_code=404, detail="Project not found")

    view = ui_state(state, viewer_id, admin=admin)
    visible_people = {person["id"]: person for person in view["people"]}
    project_record = next(project for project in view["projects"] if project["id"] == project_id)
    member_ids = [person_id for person_id in project_record["person_ids"] if person_id in visible_people]
    members = [visible_people[person_id] for person_id in member_ids]
    member_names = [person["name"] for person in members]

    meetings = [
        meeting.model_dump(mode="json")
        for meeting in sorted(state.meetings.values(), key=lambda item: item.imported_at, reverse=True)
        if not meeting.archived and (project_id in meeting.topic_ids or any(person_id in meeting.speaker_ids for person_id in member_ids))
    ][:8]

    actions = [
        _action_record(state, action)
        for action in sorted(state.actions.values(), key=lambda item: (-item.priority_score, item.title))
        if (
            action.review_status == ReviewStatus.APPROVED
            and not action.archived
            and action.owner_id in member_ids
            and can_view_action(state, action.id, viewer_id, admin=admin)
        )
    ]

    project_keywords = {keyword.lower() for keyword in project_record["keywords"]}
    followups = []
    for question in sorted(state.literature_questions.values(), key=lambda item: (-item.priority_score, item.question)):
        if question.review_status != ReviewStatus.APPROVED or question.archived:
            continue
        source_match = question.source_person_id in member_ids
        meeting_match = question.meeting_id in state.meetings and project_id in state.meetings[question.meeting_id].topic_ids
        keyword_match = bool(project_keywords & set(question.search_prompt.lower().split()))
        if source_match or meeting_match or keyword_match:
            followups.append(question.model_dump(mode="json"))
        if len(followups) >= 8:
            break

    progress = []
    for member in members:
        for update in member["recent_updates"][:3]:
            progress.append({"label": member["name"], "detail": update, "kind": "profile"})
    for action in actions[:5]:
        progress.append({"label": action["owner_name"], "detail": f"{action['title']} ({action['status'].replace('_', ' ')})", "kind": "action"})
    for meeting in meetings[:4]:
        if meeting["summary"]:
            progress.append({"label": meeting["title"], "detail": meeting["summary"], "kind": "meeting"})
    progress = progress[:10]

    open_challenges = list(project_record["open_challenges"])
    for member in members:
        open_challenges.extend(member["challenges"][:2])
    open_challenges = list(dict.fromkeys(open_challenges))[:8]

    slides = [
        {
            "kicker": "Intro",
            "title": project_record["label"],
            "body": project_record["description"] or "Project context will be filled from admin notes and approved meeting memory.",
        },
        {
            "kicker": "People",
            "title": f"{len(members)} connected members",
            "body": ", ".join(member_names[:8]) if member_names else "No members linked yet.",
        },
        {
            "kicker": "Progress",
            "title": f"{len(progress)} recent signals",
            "body": progress[0]["detail"] if progress else "No approved progress signals yet.",
        },
        {
            "kicker": "Next questions",
            "title": f"{len(open_challenges) + len(followups)} open leads",
            "body": (open_challenges or [item["question"] for item in followups] or ["No open questions recorded yet."])[0],
        },
    ]

    return {
        "view": view,
        "project": project_record,
        "members": members,
        "meetings": meetings,
        "actions": actions,
        "followups": followups,
        "progress": progress,
        "open_challenges": open_challenges,
        "slides": slides,
        "counts": {
            "members": len(members),
            "meetings": len(meetings),
            "actions": len(actions),
            "followups": len(followups),
            "progress": len(progress),
        },
    }


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    state = get_state()
    view = ui_state(state, session_person_id(request), admin=is_admin(request))
    return render(
        request,
        "index.html",
        {
            "view": view,
            "state_json": json.dumps(view),
            "active": "atlas",
        },
    )


@app.get("/projects", response_class=HTMLResponse)
def projects_page(request: Request):
    state = get_state()
    view = ui_state(state, session_person_id(request), admin=is_admin(request))
    return render(
        request,
        "projects.html",
        {
            "view": view,
            "active": "projects",
        },
    )


@app.get("/projects/{project_id}", response_class=HTMLResponse)
def project_page(project_id: str, request: Request):
    state = get_state()
    detail = project_detail_state(state, project_id, session_person_id(request), admin=is_admin(request))
    return render(
        request,
        "project.html",
        {
            **detail,
            "active": "projects",
            "active_project_id": project_id,
            "statuses": [item.value for item in ActionStatus],
        },
    )


@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    if redirect := require_member_or_admin(request):
        return redirect
    return render(
        request,
        "upload.html",
        {
            "meeting_types": [item.value for item in MeetingType],
            "active": "upload",
        },
    )


@app.post("/import")
async def import_page(
    request: Request,
    transcript: Annotated[UploadFile, File()],
    title: Annotated[str, Form()] = "",
    meeting_type: Annotated[str, Form()] = MeetingType.LAB_MEETING.value,
    meeting_date: Annotated[str, Form()] = "",
    sensitive: Annotated[bool, Form()] = False,
):
    if redirect := require_member_or_admin(request):
        return redirect
    raw = (await transcript.read()).decode("utf-8", errors="replace")
    state = get_state()
    parsed_date = date.fromisoformat(meeting_date) if meeting_date else None
    import_transcript(
        state=state,
        raw_text=raw,
        source_name=transcript.filename or "uploaded transcript",
        title=title or transcript.filename or "Imported meeting",
        meeting_type=meeting_type,
        meeting_date=parsed_date,
        sensitive=sensitive,
    )
    persist(state)
    return RedirectResponse(url="/review", status_code=303)


@app.get("/review", response_class=HTMLResponse)
def review_page(request: Request):
    if redirect := require_member_or_admin(request):
        return redirect
    state = get_state()
    return render(
        request,
        "review.html",
        {
            "view": ui_state(state, session_person_id(request), admin=is_admin(request), include_reviews=True),
            "active": "review",
        },
    )


@app.post("/review/{item_id}/approve")
def approve_review(request: Request, item_id: str, edited_text: Annotated[str, Form()] = ""):
    if redirect := require_member_or_admin(request):
        return redirect
    state = get_state()
    if item_id not in state.review_items:
        raise HTTPException(status_code=404, detail="Review item not found")
    apply_review_decision(state, item_id, ReviewStatus.APPROVED, edited_text or None)
    persist(state)
    return RedirectResponse(url="/review", status_code=303)


@app.post("/review/{item_id}/reject")
def reject_review(request: Request, item_id: str):
    if redirect := require_member_or_admin(request):
        return redirect
    state = get_state()
    if item_id not in state.review_items:
        raise HTTPException(status_code=404, detail="Review item not found")
    apply_review_decision(state, item_id, ReviewStatus.REJECTED)
    persist(state)
    return RedirectResponse(url="/review", status_code=303)


@app.get("/people/{person_id}", response_class=HTMLResponse)
def person_page(person_id: str, request: Request):
    state = get_state()
    if person_id not in state.people or state.people[person_id].archived:
        raise HTTPException(status_code=404, detail="Person not found")
    view = ui_state(state, session_person_id(request), admin=is_admin(request))
    person = next(item for item in view["people"] if item["id"] == person_id)
    return render(
        request,
        "person.html",
        {
            "person": person,
            "view": view,
            "active": "atlas",
        },
    )


@app.get("/meetings", response_class=HTMLResponse)
def meetings_page(request: Request):
    state = get_state()
    return render(
        request,
        "meetings.html",
        {
            "view": ui_state(state, session_person_id(request), admin=is_admin(request)),
            "active": "meetings",
        },
    )


@app.get("/actions", response_class=HTMLResponse)
def actions_page(request: Request):
    state = get_state()
    return render(
        request,
        "actions.html",
        {
            "view": ui_state(state, session_person_id(request), admin=is_admin(request)),
            "statuses": [item.value for item in ActionStatus],
            "active": "actions",
        },
    )


@app.post("/actions/{action_id}/status")
def update_action_status(request: Request, action_id: str, status: Annotated[str, Form()]):
    state = get_state()
    if action_id not in state.actions:
        raise HTTPException(status_code=404, detail="Action not found")
    if not is_admin(request) and not session_person_id(request):
        return RedirectResponse(url="/login", status_code=303)
    if not can_view_action(state, action_id, session_person_id(request), admin=is_admin(request)):
        raise HTTPException(status_code=404, detail="Action not found")
    state.actions[action_id].status = ActionStatus(status)
    persist(state)
    return RedirectResponse(url="/actions", status_code=303)


def admin_view(state) -> dict:
    people = sorted(state.people.values(), key=lambda item: (item.archived, item.role, item.name))
    projects = sorted(state.projects.values(), key=lambda item: (item.archived, item.kind != "sig", item.label))
    supervisor_names = {
        person.id: [state.people[supervisor_id].name for supervisor_id in person.supervisor_ids if supervisor_id in state.people]
        for person in people
    }
    supervisee_names = {
        person.id: [other.name for other in people if person.id in other.supervisor_ids]
        for person in people
    }
    action_viewers = {
        action.id: [state.people[person_id].name for person_id in action_viewer_ids(state, action.id) if person_id in state.people]
        for action in state.actions.values()
    }
    return {
        "people": people,
        "projects": projects,
        "meetings": sorted(state.meetings.values(), key=lambda item: item.imported_at, reverse=True),
        "actions": sorted(state.actions.values(), key=lambda item: (-item.priority_score, item.title)),
        "literature_questions": sorted(state.literature_questions.values(), key=lambda item: (-item.priority_score, item.question)),
        "review_items": sorted(state.review_items.values(), key=lambda item: item.created_at, reverse=True),
        "activity": list(reversed(state.activity[-40:])),
        "members_by_project": {
            project.id: [person for person in people if project.id in person.projects]
            for project in projects
        },
        "supervisor_names": supervisor_names,
        "supervisee_names": supervisee_names,
        "global_supervisors": [person for person in people if person.is_global_supervisor and not person.archived],
        "orphan_phds": [
            person
            for person in people
            if "phd" in person.role.lower() and not person.archived and not person.supervisor_ids
        ],
        "action_viewers": action_viewers,
        "counts": {
            "people": len(people),
            "archived_people": sum(1 for person in people if person.archived),
            "projects": len(projects),
            "archived_projects": sum(1 for project in projects if project.archived),
            "meetings": len(state.meetings),
            "actions": len(state.actions),
            "reviews": len(state.review_items),
        },
    }


@app.get("/login", response_class=HTMLResponse)
def member_login_page(request: Request):
    if current_person(request):
        return RedirectResponse(url="/actions", status_code=303)
    state = get_state()
    members = sorted(
        [person for person in state.people.values() if not person.archived and person.login_enabled],
        key=lambda item: item.name,
    )
    return render(
        request,
        "login.html",
        {
            "active": "login",
            "members": members,
            "error": "",
        },
    )


@app.post("/login")
def member_login(request: Request, person_id: Annotated[str, Form()], password: Annotated[str, Form()] = ""):
    state = get_state()
    person = state.people.get(person_id)
    if person and not person.archived and person.login_enabled and verify_password(password, person.password_hash):
        request.session["person_id"] = person.id
        return RedirectResponse(url="/actions", status_code=303)
    members = sorted(
        [item for item in state.people.values() if not item.archived and item.login_enabled],
        key=lambda item: item.name,
    )
    return render(
        request,
        "login.html",
        {
            "active": "login",
            "members": members,
            "error": "Incorrect member or password.",
        },
    )


@app.post("/logout")
def member_logout(request: Request):
    request.session.pop("person_id", None)
    return RedirectResponse(url="/", status_code=303)


@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    if is_admin(request):
        return RedirectResponse(url="/admin", status_code=303)
    return render(
        request,
        "admin_login.html",
        {
            "active": "admin",
            "password_configured": admin_password() is not None,
            "error": "",
        },
    )


@app.post("/admin/login")
def admin_login(request: Request, password: Annotated[str, Form()] = ""):
    configured_password = admin_password()
    if configured_password and secrets.compare_digest(password, configured_password):
        request.session["admin_authenticated"] = True
        return RedirectResponse(url="/admin", status_code=303)
    return render(
        request,
        "admin_login.html",
        {
            "active": "admin",
            "password_configured": configured_password is not None,
            "error": "Admin password is not configured." if not configured_password else "Incorrect password.",
        },
    )


@app.post("/admin/logout")
def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    return render(request, "admin_dashboard.html", {"active": "admin", "admin": admin_view(state)})


@app.get("/admin/people", response_class=HTMLResponse)
def admin_people(request: Request):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    return render(request, "admin_people.html", {"active": "admin", "admin": admin_view(state)})


@app.get("/admin/people/new", response_class=HTMLResponse)
def admin_person_new(request: Request):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    return render(
        request,
        "admin_person_form.html",
        {"active": "admin", "person": None, "admin": admin_view(state), "form_action": "/admin/people/new"},
    )


@app.post("/admin/people/new")
def admin_person_create(
    request: Request,
    name: Annotated[str, Form()],
    role: Annotated[str, Form()] = "Lab member",
    intro: Annotated[str, Form()] = "",
    source_url: Annotated[str, Form()] = "",
    topics: Annotated[str, Form()] = "",
    methods: Annotated[str, Form()] = "",
    challenges: Annotated[str, Form()] = "",
    recent_updates: Annotated[str, Form()] = "",
    project_ids: Annotated[list[str] | None, Form()] = None,
    supervisor_ids: Annotated[list[str] | None, Form()] = None,
    is_global_supervisor: Annotated[bool, Form()] = False,
    login_enabled: Annotated[bool, Form()] = False,
    member_password: Annotated[str, Form()] = "",
):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    person = upsert_person(
        state,
        name=name,
        role=role,
        intro=intro,
        source_url=source_url,
        topics=list_from_text(topics),
        methods=list_from_text(methods),
        projects=project_ids or [],
        challenges=list_from_text(challenges),
        recent_updates=list_from_text(recent_updates),
        supervisor_ids=supervisor_ids or [],
        is_global_supervisor=is_global_supervisor,
        login_enabled=login_enabled,
    )
    if member_password.strip():
        person.password_hash = hash_password(member_password)
    persist(state)
    return RedirectResponse(url="/admin/people", status_code=303)


@app.get("/admin/people/{person_id}/edit", response_class=HTMLResponse)
def admin_person_edit_page(person_id: str, request: Request):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    if person_id not in state.people:
        raise HTTPException(status_code=404, detail="Person not found")
    return render(
        request,
        "admin_person_form.html",
        {
            "active": "admin",
            "person": state.people[person_id],
            "admin": admin_view(state),
            "form_action": f"/admin/people/{person_id}/edit",
        },
    )


@app.post("/admin/people/{person_id}/edit")
def admin_person_update(
    person_id: str,
    request: Request,
    name: Annotated[str, Form()],
    role: Annotated[str, Form()] = "Lab member",
    intro: Annotated[str, Form()] = "",
    source_url: Annotated[str, Form()] = "",
    topics: Annotated[str, Form()] = "",
    methods: Annotated[str, Form()] = "",
    challenges: Annotated[str, Form()] = "",
    recent_updates: Annotated[str, Form()] = "",
    project_ids: Annotated[list[str] | None, Form()] = None,
    supervisor_ids: Annotated[list[str] | None, Form()] = None,
    is_global_supervisor: Annotated[bool, Form()] = False,
    login_enabled: Annotated[bool, Form()] = False,
    member_password: Annotated[str, Form()] = "",
):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    if person_id not in state.people:
        raise HTTPException(status_code=404, detail="Person not found")
    person = upsert_person(
        state,
        person_id=person_id,
        name=name,
        role=role,
        intro=intro,
        source_url=source_url,
        topics=list_from_text(topics),
        methods=list_from_text(methods),
        projects=project_ids or [],
        challenges=list_from_text(challenges),
        recent_updates=list_from_text(recent_updates),
        supervisor_ids=supervisor_ids or [],
        is_global_supervisor=is_global_supervisor,
        login_enabled=login_enabled,
    )
    if member_password.strip():
        person.password_hash = hash_password(member_password)
    persist(state)
    return RedirectResponse(url="/admin/people", status_code=303)


@app.post("/admin/people/{person_id}/archive")
def admin_person_archive(person_id: str, request: Request):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    if person_id not in state.people:
        raise HTTPException(status_code=404, detail="Person not found")
    set_archived(state, "people", person_id, True)
    persist(state)
    return RedirectResponse(url="/admin/people", status_code=303)


@app.post("/admin/people/{person_id}/restore")
def admin_person_restore(person_id: str, request: Request):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    if person_id not in state.people:
        raise HTTPException(status_code=404, detail="Person not found")
    set_archived(state, "people", person_id, False)
    persist(state)
    return RedirectResponse(url="/admin/people", status_code=303)


@app.get("/admin/groups", response_class=HTMLResponse)
def admin_groups(request: Request):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    return render(request, "admin_groups.html", {"active": "admin", "admin": admin_view(state)})


@app.get("/admin/groups/new", response_class=HTMLResponse)
def admin_group_new(request: Request):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    return render(
        request,
        "admin_group_form.html",
        {"active": "admin", "group": None, "admin": admin_view(state), "form_action": "/admin/groups/new"},
    )


@app.post("/admin/groups/new")
def admin_group_create(
    request: Request,
    label: Annotated[str, Form()],
    kind: Annotated[str, Form()] = "theme",
    description: Annotated[str, Form()] = "",
    keywords: Annotated[str, Form()] = "",
    open_challenges: Annotated[str, Form()] = "",
    member_ids: Annotated[list[str] | None, Form()] = None,
):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    upsert_project(
        state,
        label=label,
        kind=kind,
        description=description,
        keywords=list_from_text(keywords),
        open_challenges=list_from_text(open_challenges),
        member_ids=member_ids or [],
    )
    persist(state)
    return RedirectResponse(url="/admin/groups", status_code=303)


@app.get("/admin/groups/{group_id}/edit", response_class=HTMLResponse)
def admin_group_edit_page(group_id: str, request: Request):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    if group_id not in state.projects:
        raise HTTPException(status_code=404, detail="Group not found")
    return render(
        request,
        "admin_group_form.html",
        {
            "active": "admin",
            "group": state.projects[group_id],
            "admin": admin_view(state),
            "form_action": f"/admin/groups/{group_id}/edit",
        },
    )


@app.post("/admin/groups/{group_id}/edit")
def admin_group_update(
    group_id: str,
    request: Request,
    label: Annotated[str, Form()],
    kind: Annotated[str, Form()] = "theme",
    description: Annotated[str, Form()] = "",
    keywords: Annotated[str, Form()] = "",
    open_challenges: Annotated[str, Form()] = "",
    member_ids: Annotated[list[str] | None, Form()] = None,
):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    if group_id not in state.projects:
        raise HTTPException(status_code=404, detail="Group not found")
    upsert_project(
        state,
        project_id=group_id,
        label=label,
        kind=kind,
        description=description,
        keywords=list_from_text(keywords),
        open_challenges=list_from_text(open_challenges),
        member_ids=member_ids or [],
    )
    persist(state)
    return RedirectResponse(url="/admin/groups", status_code=303)


@app.post("/admin/groups/{group_id}/archive")
def admin_group_archive(group_id: str, request: Request):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    if group_id not in state.projects:
        raise HTTPException(status_code=404, detail="Group not found")
    set_archived(state, "projects", group_id, True)
    persist(state)
    return RedirectResponse(url="/admin/groups", status_code=303)


@app.post("/admin/groups/{group_id}/restore")
def admin_group_restore(group_id: str, request: Request):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    if group_id not in state.projects:
        raise HTTPException(status_code=404, detail="Group not found")
    set_archived(state, "projects", group_id, False)
    persist(state)
    return RedirectResponse(url="/admin/groups", status_code=303)


@app.post("/admin/groups/{group_id}/members/add")
def admin_group_member_add(group_id: str, request: Request, person_id: Annotated[str, Form()]):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    try:
        add_member_to_project(state, group_id, person_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Group or person not found") from None
    persist(state)
    return RedirectResponse(url=f"/admin/groups/{group_id}/edit", status_code=303)


@app.post("/admin/groups/{group_id}/members/{person_id}/remove")
def admin_group_member_remove(group_id: str, person_id: str, request: Request):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    try:
        remove_member_from_project(state, group_id, person_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Group or person not found") from None
    persist(state)
    return RedirectResponse(url=f"/admin/groups/{group_id}/edit", status_code=303)


@app.get("/admin/content", response_class=HTMLResponse)
def admin_content(request: Request):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    return render(
        request,
        "admin_content.html",
        {
            "active": "admin",
            "admin": admin_view(state),
            "meeting_types": [item.value for item in MeetingType],
            "action_statuses": [item.value for item in ActionStatus],
            "review_statuses": [item.value for item in ReviewStatus],
        },
    )


@app.post("/admin/meetings/{meeting_id}/edit")
def admin_meeting_update(
    meeting_id: str,
    request: Request,
    title: Annotated[str, Form()],
    meeting_type: Annotated[str, Form()] = MeetingType.LAB_MEETING.value,
    meeting_date: Annotated[str, Form()] = "",
    summary: Annotated[str, Form()] = "",
    sensitive: Annotated[bool, Form()] = False,
):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    if meeting_id not in state.meetings:
        raise HTTPException(status_code=404, detail="Meeting not found")
    meeting = state.meetings[meeting_id]
    meeting.title = title.strip()
    meeting.meeting_type = MeetingType(meeting_type)
    meeting.meeting_date = date.fromisoformat(meeting_date) if meeting_date else None
    meeting.summary = summary.strip()
    meeting.sensitive = sensitive
    persist(state)
    return RedirectResponse(url="/admin/content", status_code=303)


@app.post("/admin/actions/{action_id}/edit")
def admin_action_update(
    action_id: str,
    request: Request,
    title: Annotated[str, Form()],
    status: Annotated[str, Form()] = ActionStatus.OPEN.value,
    review_status: Annotated[str, Form()] = ReviewStatus.APPROVED.value,
    owner_id: Annotated[str, Form()] = "",
):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    if action_id not in state.actions:
        raise HTTPException(status_code=404, detail="Action not found")
    action = state.actions[action_id]
    action.title = title.strip()
    action.status = ActionStatus(status)
    action.review_status = ReviewStatus(review_status)
    action.owner_id = owner_id if owner_id in state.people else None
    for person in state.people.values():
        if action.id in person.action_ids and person.id != action.owner_id:
            person.action_ids.remove(action.id)
    if action.owner_id and action.review_status == ReviewStatus.APPROVED:
        state.people[action.owner_id].action_ids = unique_extend(state.people[action.owner_id].action_ids, [action.id])
    persist(state)
    return RedirectResponse(url="/admin/content", status_code=303)


@app.post("/admin/literature/{question_id}/edit")
def admin_literature_update(
    question_id: str,
    request: Request,
    question: Annotated[str, Form()],
    search_prompt: Annotated[str, Form()] = "",
    review_status: Annotated[str, Form()] = ReviewStatus.APPROVED.value,
):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    if question_id not in state.literature_questions:
        raise HTTPException(status_code=404, detail="Literature question not found")
    item = state.literature_questions[question_id]
    item.question = question.strip()
    item.search_prompt = search_prompt.strip()
    item.review_status = ReviewStatus(review_status)
    persist(state)
    return RedirectResponse(url="/admin/content", status_code=303)


@app.post("/admin/reviews/{item_id}/edit")
def admin_review_update(
    item_id: str,
    request: Request,
    title: Annotated[str, Form()],
    proposed_text: Annotated[str, Form()] = "",
    status: Annotated[str, Form()] = ReviewStatus.PENDING.value,
):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    if item_id not in state.review_items:
        raise HTTPException(status_code=404, detail="Review item not found")
    item = state.review_items[item_id]
    item.title = title.strip()
    item.proposed_text = proposed_text.strip()
    item.status = ReviewStatus(status)
    persist(state)
    return RedirectResponse(url="/admin/content", status_code=303)


@app.post("/admin/{collection}/{item_id}/archive")
def admin_content_archive(collection: str, item_id: str, request: Request):
    if redirect := require_admin(request):
        return redirect
    allowed = {"meetings", "actions", "literature_questions", "review_items"}
    if collection not in allowed:
        raise HTTPException(status_code=404, detail="Collection not found")
    state = get_state()
    records = getattr(state, collection)
    if item_id not in records:
        raise HTTPException(status_code=404, detail="Record not found")
    set_archived(state, collection, item_id, True)
    persist(state)
    return RedirectResponse(url="/admin/content", status_code=303)


@app.post("/admin/{collection}/{item_id}/restore")
def admin_content_restore(collection: str, item_id: str, request: Request):
    if redirect := require_admin(request):
        return redirect
    allowed = {"meetings", "actions", "literature_questions", "review_items"}
    if collection not in allowed:
        raise HTTPException(status_code=404, detail="Collection not found")
    state = get_state()
    records = getattr(state, collection)
    if item_id not in records:
        raise HTTPException(status_code=404, detail="Record not found")
    set_archived(state, collection, item_id, False)
    persist(state)
    return RedirectResponse(url="/admin/content", status_code=303)


@app.get("/api/state")
def api_state(request: Request):
    return ui_state(get_state(), session_person_id(request), admin=is_admin(request))


@app.get("/api/export")
def api_export(request: Request):
    if redirect := require_admin(request):
        return redirect
    state = get_state()
    path = export_state_snapshot(state, DATA_DIR / "exports")
    return FileResponse(path, media_type="application/json", filename=path.name)
