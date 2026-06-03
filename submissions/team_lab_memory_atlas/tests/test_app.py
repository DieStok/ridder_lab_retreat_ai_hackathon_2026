from __future__ import annotations

from fastapi.testclient import TestClient

import app as atlas_app
from lab_memory_atlas.auth import hash_password
from lab_memory_atlas.models import ActionItem, ReviewStatus


SAMPLE_TRANSCRIPT = """WEBVTT

00:00:01.000 --> 00:00:04.000
<v Franka>We should ask Christian to run cell typing for the spatial transcriptomics data.</v>

00:00:05.000 --> 00:00:08.000
<v Ahmadreza>I'll compare foundation model embeddings and read the benchmark paper.</v>
"""


def test_html_pages_render(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(atlas_app, "DATA_DIR", tmp_path)
    client = TestClient(atlas_app.app)

    for path in ["/", "/login", "/actions", "/meetings", "/projects", "/projects/foundation-models"]:
        response = client.get(path)
        assert response.status_code == 200
        assert "Lab Memory Atlas" in response.text
        assert "de ridder lab" in response.text
        assert "de-ridder-lab-knight.svg" in response.text

    for path in ["/review", "/upload"]:
        response = client.get(path, follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/login"

    for path in ["/api/export"]:
        response = client.get(path, follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/admin/login"


def test_transcript_import_endpoint_creates_review_items(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(atlas_app, "DATA_DIR", tmp_path)
    client = TestClient(atlas_app.app)
    login_admin(client, monkeypatch)

    response = client.post(
        "/import",
        data={"title": "Demo SIG", "meeting_type": "sig"},
        files={"transcript": ("demo.vtt", SAMPLE_TRANSCRIPT, "text/plain")},
        follow_redirects=False,
    )

    assert response.status_code == 303
    state_response = client.get("/api/state")
    assert state_response.status_code == 200
    assert state_response.json()["counts"]["meetings"] == 1
    assert state_response.json()["counts"]["pending_reviews"] > 0


def enable_member_login(tmp_path, monkeypatch, person_id: str = "ahmadreza-iranpour", password: str = "member-pin") -> None:
    monkeypatch.setattr(atlas_app, "DATA_DIR", tmp_path)
    state = atlas_app.get_state()
    state.people[person_id].login_enabled = True
    state.people[person_id].password_hash = hash_password(password)
    atlas_app.persist(state)


def test_logged_in_member_can_import_and_review_changes(tmp_path, monkeypatch) -> None:
    enable_member_login(tmp_path, monkeypatch)
    client = TestClient(atlas_app.app)
    login_member(client, "ahmadreza-iranpour", "member-pin")

    upload_page = client.get("/upload")
    assert upload_page.status_code == 200
    assert "Add a meeting transcript" in upload_page.text

    response = client.post(
        "/import",
        data={"title": "Member SIG", "meeting_type": "sig"},
        files={"transcript": ("member-demo.vtt", SAMPLE_TRANSCRIPT, "text/plain")},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/review"

    review_page = client.get("/review")
    assert review_page.status_code == 200
    assert "draft updates" in review_page.text

    state = atlas_app.get_state()
    pending_ids = [item.id for item in state.review_items.values() if item.status == ReviewStatus.PENDING]
    assert len(pending_ids) >= 2

    approved = client.post(f"/review/{pending_ids[0]}/approve", data={"edited_text": ""}, follow_redirects=False)
    rejected = client.post(f"/review/{pending_ids[1]}/reject", follow_redirects=False)

    assert approved.status_code == 303
    assert rejected.status_code == 303
    updated_state = atlas_app.get_state()
    assert updated_state.review_items[pending_ids[0]].status == ReviewStatus.APPROVED
    assert updated_state.review_items[pending_ids[1]].status == ReviewStatus.REJECTED


def login_admin(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("LAB_ATLAS_ADMIN_PASSWORD", "test-admin-pass")
    response = client.post("/admin/login", data={"password": "test-admin-pass"}, follow_redirects=False)
    assert response.status_code == 303


def test_admin_requires_login_and_accepts_configured_password(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(atlas_app, "DATA_DIR", tmp_path)
    monkeypatch.setenv("LAB_ATLAS_ADMIN_PASSWORD", "test-admin-pass")
    client = TestClient(atlas_app.app)

    blocked = client.get("/admin", follow_redirects=False)
    assert blocked.status_code == 303
    assert blocked.headers["location"] == "/admin/login"

    wrong = client.post("/admin/login", data={"password": "wrong"})
    assert wrong.status_code == 200
    assert "Incorrect password" in wrong.text

    login_admin(client, monkeypatch)
    allowed = client.get("/admin")
    assert allowed.status_code == 200
    assert "Atlas control room" in allowed.text


def test_admin_can_add_group_add_person_and_archive_person(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(atlas_app, "DATA_DIR", tmp_path)
    client = TestClient(atlas_app.app)
    login_admin(client, monkeypatch)

    group_response = client.post(
        "/admin/groups/new",
        data={
            "label": "Test SIG",
            "kind": "sig",
            "description": "Temporary test group",
            "keywords": "test\nmethods",
        },
        follow_redirects=False,
    )
    assert group_response.status_code == 303

    person_response = client.post(
        "/admin/people/new",
        data={
            "name": "Test Member",
            "role": "PhD Student",
            "intro": "Works on test methods.",
            "topics": "test methods",
            "project_ids": ["test-sig"],
            "supervisor_ids": ["jeroen-de-ridder"],
            "login_enabled": "true",
            "member_password": "test-member-pin",
        },
        follow_redirects=False,
    )
    assert person_response.status_code == 303

    state_response = client.get("/api/state")
    assert state_response.status_code == 200
    state = state_response.json()
    assert any(person["name"] == "Test Member" for person in state["people"])
    test_group = next(group for group in state["projects"] if group["id"] == "test-sig")
    assert "test-member" in test_group["person_ids"]

    archive_response = client.post("/admin/people/test-member/archive", follow_redirects=False)
    assert archive_response.status_code == 303
    filtered_state = client.get("/api/state").json()
    assert all(person["id"] != "test-member" for person in filtered_state["people"])

    admin_people = client.get("/admin/people")
    assert admin_people.status_code == 200
    assert "Test Member" in admin_people.text
    assert "login enabled" in admin_people.text


def test_admin_group_membership_remove_updates_public_group(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(atlas_app, "DATA_DIR", tmp_path)
    client = TestClient(atlas_app.app)
    login_admin(client, monkeypatch)

    response = client.post(
        "/admin/groups/sig-ai-foundationmodels/members/ahmadreza-iranpour/remove",
        follow_redirects=False,
    )
    assert response.status_code == 303

    state = client.get("/api/state").json()
    group = next(group for group in state["projects"] if group["id"] == "sig-ai-foundationmodels")
    person = next(person for person in state["people"] if person["id"] == "ahmadreza-iranpour")
    assert "ahmadreza-iranpour" not in group["person_ids"]
    assert "sig-ai-foundationmodels" not in person["projects"]


def setup_private_action(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(atlas_app, "DATA_DIR", tmp_path)
    state = atlas_app.get_state()
    for person_id, password in {
        "ahmadreza-iranpour": "owner-pin",
        "franka-rang": "supervisor-pin",
        "jeroen-de-ridder": "pi-pin",
        "carlos-garcia-fernandez": "other-pin",
    }.items():
        state.people[person_id].login_enabled = True
        state.people[person_id].password_hash = hash_password(password)
    state.people["ahmadreza-iranpour"].supervisor_ids = ["franka-rang"]
    state.actions["private-action"] = ActionItem(
        id="private-action",
        owner_id="ahmadreza-iranpour",
        title="Compare private embeddings",
        meeting_id="manual",
        review_status=ReviewStatus.APPROVED,
        priority_score=8,
    )
    state.people["ahmadreza-iranpour"].action_ids.append("private-action")
    atlas_app.persist(state)


def action_titles(client: TestClient) -> list[str]:
    response = client.get("/api/state")
    assert response.status_code == 200
    return [item["title"] for item in response.json()["actions"]]


def login_member(client: TestClient, person_id: str, password: str) -> None:
    response = client.post("/login", data={"person_id": person_id, "password": password}, follow_redirects=False)
    assert response.status_code == 303


def test_private_actions_are_visible_only_to_owner_supervisors_pi_and_admin(tmp_path, monkeypatch) -> None:
    setup_private_action(tmp_path, monkeypatch)

    anonymous = TestClient(atlas_app.app)
    assert "Compare private embeddings" not in action_titles(anonymous)

    owner = TestClient(atlas_app.app)
    login_member(owner, "ahmadreza-iranpour", "owner-pin")
    assert "Compare private embeddings" in action_titles(owner)

    supervisor = TestClient(atlas_app.app)
    login_member(supervisor, "franka-rang", "supervisor-pin")
    assert "Compare private embeddings" in action_titles(supervisor)

    pi = TestClient(atlas_app.app)
    login_member(pi, "jeroen-de-ridder", "pi-pin")
    assert "Compare private embeddings" in action_titles(pi)

    unrelated = TestClient(atlas_app.app)
    login_member(unrelated, "carlos-garcia-fernandez", "other-pin")
    assert "Compare private embeddings" not in action_titles(unrelated)

    admin = TestClient(atlas_app.app)
    login_admin(admin, monkeypatch)
    assert "Compare private embeddings" in action_titles(admin)


def test_action_status_update_requires_visibility(tmp_path, monkeypatch) -> None:
    setup_private_action(tmp_path, monkeypatch)

    anonymous = TestClient(atlas_app.app)
    blocked = anonymous.post("/actions/private-action/status", data={"status": "done"}, follow_redirects=False)
    assert blocked.status_code == 303
    assert blocked.headers["location"] == "/login"

    unrelated = TestClient(atlas_app.app)
    login_member(unrelated, "carlos-garcia-fernandez", "other-pin")
    not_found = unrelated.post("/actions/private-action/status", data={"status": "done"}, follow_redirects=False)
    assert not_found.status_code == 404

    owner = TestClient(atlas_app.app)
    login_member(owner, "ahmadreza-iranpour", "owner-pin")
    updated = owner.post("/actions/private-action/status", data={"status": "done"}, follow_redirects=False)
    assert updated.status_code == 303


def test_project_page_filters_private_actions_by_viewer(tmp_path, monkeypatch) -> None:
    setup_private_action(tmp_path, monkeypatch)

    anonymous = TestClient(atlas_app.app)
    anonymous_page = anonymous.get("/projects/spatial-transcriptomics")
    assert anonymous_page.status_code == 200
    assert "Compare private embeddings" not in anonymous_page.text
    assert "Private actions require login" in anonymous_page.text

    owner = TestClient(atlas_app.app)
    login_member(owner, "ahmadreza-iranpour", "owner-pin")
    owner_page = owner.get("/projects/spatial-transcriptomics")
    assert owner_page.status_code == 200
    assert "Compare private embeddings" in owner_page.text

    unrelated = TestClient(atlas_app.app)
    login_member(unrelated, "carlos-garcia-fernandez", "other-pin")
    unrelated_page = unrelated.get("/projects/spatial-transcriptomics")
    assert unrelated_page.status_code == 200
    assert "Compare private embeddings" not in unrelated_page.text

    admin = TestClient(atlas_app.app)
    login_admin(admin, monkeypatch)
    admin_page = admin.get("/projects/spatial-transcriptomics")
    assert admin_page.status_code == 200
    assert "Compare private embeddings" in admin_page.text
