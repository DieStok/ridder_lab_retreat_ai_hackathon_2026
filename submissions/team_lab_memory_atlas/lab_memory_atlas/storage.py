from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

from .models import (
    ActionStatus,
    ActivityEvent,
    AppState,
    Person,
    ProjectTopic,
    ReviewItemType,
    ReviewStatus,
    utc_now,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "data" / "demo"
STATE_FILE = "state.json"
CURRENT_SEED_VERSION = 4
GLOBAL_SUPERVISOR_IDS = {"jeroen-de-ridder"}
PERSON_ALIASES = {
    "paul": "paul-cozmuta",
}
FOUNDATION_CONTEXT = {
    "foundation-models": {
        "description": (
            "Transcriptomic foundation-model work centered on LeJEPA, a dual Set Transformer for gene-expression data. "
            "The project compares LeJEPA with Transformer, autoencoder, BulkRNABERT, raw-expression, pooled-embedding, "
            "random-forest, and bilinear downstream-head baselines across RNA-seq benchmarks and external validation tasks."
        ),
        "keywords": [
            "LeJEPA",
            "transcriptomic foundation model",
            "dual Set Transformer",
            "gene expression",
            "TCGA",
            "ARCHS4",
            "bilinear low-rank transfer head",
            "BulkRNABERT",
            "Figure 2 benchmarking",
            "Figure 3 downstream benchmark",
            "STS external validation",
            "mutation prediction",
            "survival analysis",
            "treatment response",
        ],
        "open_challenges": [
            "Complete and verify Figure 2 foundation-model benchmarking outputs, including missing expected metrics.",
            "Finalize Figure 3 downstream task benchmarking across prognosis, treatment response, mutation prediction, c-index, and external sarcoma validation branches.",
            "Verify final sample counts, figure completeness, and manuscript placeholders before the paper is considered mature.",
            "Standardize the final naming and positioning of the bilinear low-rank transfer head.",
            "Keep heavy LeJEPA extraction, retraining, and downstream sweeps on Slurm jobs, respecting Slurm-provided CUDA_VISIBLE_DEVICES.",
        ],
    },
    "sig-ai-foundationmodels": {
        "description": (
            "SIG for AI and foundation-model work, including LeJEPA, transcriptomic representation learning, "
            "foundation-model benchmarking, downstream task design, bilinear heads, and reproducible HPC workflows."
        ),
        "keywords": [
            "AI",
            "foundation model",
            "LeJEPA",
            "embedding",
            "self-supervised learning",
            "TCGA",
            "ARCHS4",
            "downstream benchmarking",
            "bilinear heads",
            "Slurm",
        ],
        "open_challenges": [
            "Coordinate benchmark design and artifact policies for foundation-model comparison runs.",
            "Share reproducibility conventions for GPU jobs, run folders, checkpoints, and downstream outputs.",
            "Track open manuscript and figure questions around LeJEPA, bilinear heads, and external validation.",
        ],
    },
}


SIG_PROJECTS = {
    "sig-ml-for-omics": ProjectTopic(
        id="sig-ml-for-omics",
        label="sig-ml_for_omics",
        kind="sig",
        description="Slack SIG for machine learning methods and omics applications.",
        keywords=["machine learning", "omics", "statistics", "model", "benchmark"],
    ),
    "sig-ai-foundationmodels": ProjectTopic(
        id="sig-ai-foundationmodels",
        label="sig-ai_foundationmodels",
        kind="sig",
        description="Slack SIG for AI and foundation-model work in the lab.",
        keywords=["AI", "foundation model", "embedding", "self-supervised", "benchmark"],
    ),
    "sig-modcall-liquidbiopsy": ProjectTopic(
        id="sig-modcall-liquidbiopsy",
        label="sig-modcall_liquidbiopsy",
        kind="sig",
        description="Slack SIG for modcall, nanopore, methylation, and liquid biopsy topics.",
        keywords=["modcall", "liquid biopsy", "nanopore", "methylation", "cfDNA"],
    ),
}


SIG_MEMBERS = {
    "sig-ml-for-omics": [
        "Amalia Tsakali",
        "Carlo Vermeulen",
        "Chiara Fiorenzani",
        "Claudio Novella Rausell",
        "Cristian Ruiz Moreno",
        "Franka Rang",
        "Jack Jiang",
        "Jeroen de Ridder",
        "Lars de Groot",
        "Lucia Barbadilla",
        "Marta Moreno Gonzalez",
        "Michiel Thieke",
        "Myrthe Jager",
        "Paul Cozmuta",
        "Roy Straver",
    ],
    "sig-ai-foundationmodels": [
        "Adrien Melquiond",
        "Ahmadreza Iranpour",
        "Carlos Garcia Fernandez",
        "Dieter Stoker",
        "Franka Rang",
        "Jeroen de Ridder",
        "Joske Ubels",
        "Karol Rogozinski",
        "Lisa de Groot",
        "Lucia Barbadilla",
        "Roy Straver",
    ],
    "sig-modcall-liquidbiopsy": [
        "Carlo Vermeulen",
        "Huub van der Ent",
        "Jack Jiang",
        "Jeroen de Ridder",
        "Jon Brugger",
        "Lucia Barbadilla",
        "Merel Jongmans",
        "Myrthe Jager",
        "Roy Straver",
        "Tristan Achterberg",
    ],
}


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "unknown"


def unique_extend(existing: list[str], new_items: Iterable[str], limit: int | None = None) -> list[str]:
    seen = {item.lower() for item in existing}
    merged = list(existing)
    for item in new_items:
        item = item.strip()
        if not item or item.lower() in seen:
            continue
        merged.append(item)
        seen.add(item.lower())
    return merged[:limit] if limit else merged


def list_from_text(value: str) -> list[str]:
    parts = re.split(r"[\n,]+", value or "")
    return [part.strip() for part in parts if part.strip()]


def unique_record_id(label: str, existing: Iterable[str]) -> str:
    base = slugify(label)
    candidate = base
    counter = 2
    existing_ids = set(existing)
    while candidate in existing_ids:
        candidate = f"{base}-{counter}"
        counter += 1
    return candidate


def state_path(data_dir: Path | None = None) -> Path:
    return (data_dir or DEFAULT_DATA_DIR) / STATE_FILE


def load_state(data_dir: Path | None = None) -> AppState:
    path = state_path(data_dir)
    if not path.exists():
        state = seed_state()
        save_state(state, data_dir)
        return state
    state = AppState.model_validate_json(path.read_text(encoding="utf-8"))
    if state.seed_version < CURRENT_SEED_VERSION:
        ensure_sig_seed_data(state)
        merge_person_aliases(state)
        ensure_foundation_context(state)
        ensure_hierarchy_defaults(state)
        state.seed_version = CURRENT_SEED_VERSION
        save_state(state, data_dir)
    return state


def save_state(state: AppState, data_dir: Path | None = None) -> None:
    path = state_path(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    state.generated_at = utc_now()
    path.write_text(json.dumps(state.model_dump(mode="json"), indent=2), encoding="utf-8")


def seed_state() -> AppState:
    people = {
        slugify(name): Person(
            id=slugify(name),
            name=name,
            role=role,
            intro="Public lab roster profile. Meeting-approved updates will fill current work, challenges, and collaboration links.",
            topics=topics,
            projects=projects,
        )
        for name, role, topics, projects in [
            ("Jeroen de Ridder", "Principal Investigator / Full Professor", ["bioinformatics", "machine learning", "cancer genomics"], ["omics-ml-impact"]),
            ("Adrien Melquiond", "Assistant Professor", ["machine learning", "omics integration"], ["omics-ml-impact"]),
            ("Carlo Vermeulen", "Assistant Professor", ["clinical diagnostics", "cancer genomics"], ["next-generation-diagnostics"]),
            ("Roy Straver", "Senior Scientist", ["nanopore sequencing", "cfDNA"], ["next-generation-diagnostics"]),
            ("Myrthe Jager", "PostDoc", ["single-cell", "tumor evolution"], ["single-cell-multiomics"]),
            ("Michiel Thieke", "PostDoc", ["machine learning", "spatial omics"], ["foundation-models"]),
            ("Franka Rang", "PostDoc", ["spatial transcriptomics", "foundation models"], ["spatial-transcriptomics"]),
            ("Joske Ubels", "PostDoc", ["treatment response", "machine learning"], ["treatment-response"]),
            ("Cristian Ruiz Moreno", "PostDoc", ["foundation models", "omics integration"], ["foundation-models"]),
            ("Lucia Barbadilla", "PhD Student", ["cancer genomics", "omics"], ["omics-ml-impact"]),
            ("Dieter Stoker", "PhD Student", ["machine learning", "research software"], ["hpc-research-infrastructure"]),
            ("Huub van der Ent", "PhD Student", ["genomics", "data integration"], ["omics-ml-impact"]),
            ("Ahmadreza Iranpour", "PhD Student", ["spatial transcriptomics", "foundation models"], ["spatial-transcriptomics"]),
            ("Carlos Garcia Fernandez", "PhD Student", ["machine learning", "diagnostics"], ["next-generation-diagnostics"]),
            ("Cas Kranenburg", "Research Technician", ["lab support", "sequencing"], ["next-generation-diagnostics"]),
            ("Emmy Wesdorp", "PhD Student", ["cancer genomics", "machine learning"], ["omics-ml-impact"]),
            ("Tristan Achterberg", "PhD Student", ["foundation models", "clinical translation"], ["foundation-models"]),
            ("Lisa de Groot", "PhD Student", ["omics integration", "statistics"], ["omics-ml-impact"]),
            ("Li-Ting Chen", "PhD Student", ["single-cell", "tumor evolution"], ["single-cell-multiomics"]),
            ("Alexandra Danyi", "PhD Student", ["liquid biopsy", "classification"], ["next-generation-diagnostics"]),
        ]
    }
    projects = {
        "omics-ml-impact": ProjectTopic(
            id="omics-ml-impact",
            label="Omics ML with impact",
            kind="theme",
            description="Machine learning and AI methods for modern omics data analysis and cancer biology.",
            keywords=["machine learning", "omics", "AI", "statistics", "cancer genomics"],
        ),
        "next-generation-diagnostics": ProjectTopic(
            id="next-generation-diagnostics",
            label="Next-generation diagnostics",
            kind="theme",
            description="Clinical diagnostic models, liquid biopsy, nanopore sequencing, and treatment personalization.",
            keywords=["diagnostics", "cfDNA", "nanopore", "liquid biopsy", "classification", "methylation"],
        ),
        "foundation-models": ProjectTopic(
            id="foundation-models",
            label="Foundation models",
            kind="theme",
            description=FOUNDATION_CONTEXT["foundation-models"]["description"],
            keywords=FOUNDATION_CONTEXT["foundation-models"]["keywords"],
            open_challenges=FOUNDATION_CONTEXT["foundation-models"]["open_challenges"],
        ),
        "spatial-transcriptomics": ProjectTopic(
            id="spatial-transcriptomics",
            label="Spatial transcriptomics",
            kind="theme",
            description="Spatial omics analysis, image-based embeddings, cell typing, and multimodal tissue context.",
            keywords=["spatial", "transcriptomics", "cell type", "image", "proteomics"],
        ),
        "single-cell-multiomics": ProjectTopic(
            id="single-cell-multiomics",
            label="Single-cell and multi-omics",
            kind="theme",
            description="Single-cell analysis, lineage tracing, data integration, and tumor evolution.",
            keywords=["single-cell", "multi-omics", "lineage", "tumor evolution", "integration"],
        ),
        "treatment-response": ProjectTopic(
            id="treatment-response",
            label="Treatment response",
            kind="theme",
            description="Predictive models for treatment benefit and clinical trial data.",
            keywords=["treatment", "response", "drug", "clinical trial", "classifier"],
        ),
        "genome-structure": ProjectTopic(
            id="genome-structure",
            label="Genome structure and epigenetics",
            kind="theme",
            description="3D genome conformation, epigenetic regulation, and non-coding variants.",
            keywords=["3D genome", "epigenetics", "chromatin", "structural variant", "Hi-C"],
        ),
        "hpc-research-infrastructure": ProjectTopic(
            id="hpc-research-infrastructure",
            label="HPC and research infrastructure",
            kind="capability",
            description="Compute workflows, reproducible research tooling, and shared lab automation.",
            keywords=["HPC", "software", "workflow", "automation", "reproducibility"],
        ),
    }
    state = AppState(people=people, projects=projects)
    ensure_sig_seed_data(state)
    merge_person_aliases(state)
    ensure_foundation_context(state)
    ensure_hierarchy_defaults(state)
    state.seed_version = CURRENT_SEED_VERSION
    refresh_project_people(state)
    refresh_helpers(state)
    state.activity.append(
        ActivityEvent(
            id="seed-roster",
            label="Seeded lab roster",
            detail="Loaded public people/project starter data from the De Ridder Lab website.",
        )
    )
    return state


def ensure_sig_seed_data(state: AppState) -> bool:
    changed = False
    for project_id, project in SIG_PROJECTS.items():
        current = state.projects.get(project_id)
        if current is None:
            state.projects[project_id] = project.model_copy(deep=True)
            changed = True
        elif current.archived:
            continue
        else:
            if current.label != project.label:
                current.label = project.label
                changed = True
            if current.kind != project.kind:
                current.kind = project.kind
                changed = True
            if current.description != project.description:
                current.description = project.description
                changed = True
            current.keywords = unique_extend(current.keywords, project.keywords)

    for project_id, members in SIG_MEMBERS.items():
        for member_name in members:
            person_id = slugify(member_name)
            if person_id not in state.people:
                state.people[person_id] = Person(
                    id=person_id,
                    name=member_name,
                    role="Lab member",
                    intro="Added from SIG membership. Meeting-approved updates will fill current work, challenges, and collaboration links.",
                    topics=sig_topics_for_member(member_name),
                    projects=[project_id],
                )
                changed = True
                continue
            person = state.people[person_id]
            if person.archived:
                continue
            if project_id not in person.projects:
                person.projects.append(project_id)
                changed = True
            original_topics = list(person.topics)
            person.topics = unique_extend(person.topics, sig_topics_for_member(member_name), limit=18)
            if person.topics != original_topics:
                changed = True

    refresh_project_people(state)
    refresh_helpers(state)
    return changed


def ensure_foundation_context(state: AppState) -> bool:
    changed = False
    for project_id, context in FOUNDATION_CONTEXT.items():
        if project_id not in state.projects:
            continue
        project = state.projects[project_id]
        if project.archived:
            continue
        if project.description != context["description"]:
            project.description = context["description"]
            changed = True
        keywords = list(context["keywords"])
        if project.keywords != keywords:
            project.keywords = keywords
            changed = True
        challenges = list(context["open_challenges"])
        if project.open_challenges != challenges:
            project.open_challenges = challenges
            changed = True
    return changed


def ensure_hierarchy_defaults(state: AppState) -> bool:
    changed = False
    for person_id, person in state.people.items():
        original_supervisors = list(person.supervisor_ids)
        person.supervisor_ids = [
            supervisor_id
            for supervisor_id in dict.fromkeys(person.supervisor_ids)
            if supervisor_id in state.people and supervisor_id != person_id
        ]
        if person.supervisor_ids != original_supervisors:
            changed = True
        should_be_global = person_id in GLOBAL_SUPERVISOR_IDS
        if person.is_global_supervisor != should_be_global and should_be_global:
            person.is_global_supervisor = True
            changed = True
    return changed


def merge_person_aliases(state: AppState) -> bool:
    changed = False
    for alias_id, canonical_id in PERSON_ALIASES.items():
        if alias_id == canonical_id or alias_id not in state.people:
            continue
        alias = state.people.pop(alias_id)
        canonical = state.people.get(canonical_id)
        if canonical is None:
            alias.id = canonical_id
            alias.name = "Paul Cozmuta" if canonical_id == "paul-cozmuta" else alias.name
            state.people[canonical_id] = alias
            canonical = alias
        else:
            canonical.topics = unique_extend(canonical.topics, alias.topics, limit=18)
            canonical.methods = unique_extend(canonical.methods, alias.methods, limit=12)
            canonical.projects = unique_extend(canonical.projects, alias.projects)
            canonical.challenges = unique_extend(canonical.challenges, alias.challenges, limit=8)
            canonical.recent_updates = unique_extend(canonical.recent_updates, alias.recent_updates, limit=12)
            canonical.action_ids = unique_extend(canonical.action_ids, alias.action_ids)
            canonical.helper_ids = unique_extend(canonical.helper_ids, alias.helper_ids)
            canonical.supervisor_ids = unique_extend(canonical.supervisor_ids, alias.supervisor_ids)
            if not canonical.intro and alias.intro:
                canonical.intro = alias.intro
            if canonical.role == "Lab member" and alias.role != "Lab member":
                canonical.role = alias.role
            if not canonical.login_enabled and alias.login_enabled:
                canonical.login_enabled = True
                canonical.password_hash = alias.password_hash
            if canonical.last_seen_meeting_id is None:
                canonical.last_seen_meeting_id = alias.last_seen_meeting_id
            canonical.archived = canonical.archived and alias.archived
        _replace_person_id_references(state, alias_id, canonical_id)
        state.activity.append(
            ActivityEvent(
                id=f"merge-person-{alias_id}",
                label="Merged duplicate person",
                detail=f"{alias.name} -> {canonical.name}",
                person_id=canonical_id,
            )
        )
        changed = True
    if changed:
        refresh_project_people(state)
        refresh_helpers(state)
    return changed


def _replace_person_id_references(state: AppState, old_id: str, new_id: str) -> None:
    for person in state.people.values():
        person.action_ids = _replace_id_list(person.action_ids, old_id, new_id)
        person.helper_ids = [person_id for person_id in _replace_id_list(person.helper_ids, old_id, new_id) if person_id != person.id]
        person.supervisor_ids = [person_id for person_id in _replace_id_list(person.supervisor_ids, old_id, new_id) if person_id != person.id]
    for project in state.projects.values():
        project.person_ids = _replace_id_list(project.person_ids, old_id, new_id)
    for meeting in state.meetings.values():
        meeting.speaker_ids = _replace_id_list(meeting.speaker_ids, old_id, new_id)
    for action in state.actions.values():
        if action.owner_id == old_id:
            action.owner_id = new_id
    for question in state.literature_questions.values():
        if question.source_person_id == old_id:
            question.source_person_id = new_id
    for review in state.review_items.values():
        if review.target_id == old_id:
            review.target_id = new_id
        review.payload = _replace_payload_id(review.payload, old_id, new_id)
    for event in state.activity:
        if event.person_id == old_id:
            event.person_id = new_id


def _replace_id_list(values: list[str], old_id: str, new_id: str) -> list[str]:
    return list(dict.fromkeys(new_id if value == old_id else value for value in values))


def _replace_payload_id(value, old_id: str, new_id: str):
    if value == old_id:
        return new_id
    if isinstance(value, list):
        return [_replace_payload_id(item, old_id, new_id) for item in value]
    if isinstance(value, dict):
        return {key: _replace_payload_id(item, old_id, new_id) for key, item in value.items()}
    return value


def sig_topics_for_member(member_name: str) -> list[str]:
    member_id = slugify(member_name)
    topics: list[str] = []
    for project_id, members in SIG_MEMBERS.items():
        if member_id in {slugify(member) for member in members}:
            topics.extend(SIG_PROJECTS[project_id].keywords[:2])
    return unique_extend([], topics, limit=8)


def refresh_project_people(state: AppState) -> None:
    for project in state.projects.values():
        project.person_ids = []
    for person in state.people.values():
        if person.archived:
            continue
        for project_id in person.projects:
            if (
                project_id in state.projects
                and not state.projects[project_id].archived
                and person.id not in state.projects[project_id].person_ids
            ):
                state.projects[project_id].person_ids.append(person.id)


def refresh_helpers(state: AppState) -> None:
    for person in state.people.values():
        if person.archived:
            person.helper_ids = []
            continue
        scores: list[tuple[int, str]] = []
        own_terms = set(term.lower() for term in person.topics + person.methods + person.projects)
        for other in state.people.values():
            if other.id == person.id or other.archived:
                continue
            other_terms = set(term.lower() for term in other.topics + other.methods + other.projects)
            overlap = len(own_terms & other_terms)
            if overlap:
                scores.append((overlap, other.id))
        person.helper_ids = [person_id for _, person_id in sorted(scores, reverse=True)[:4]]


def log_activity(
    state: AppState,
    label: str,
    detail: str = "",
    person_id: str | None = None,
    meeting_id: str | None = None,
) -> None:
    state.activity.append(
        ActivityEvent(
            id=f"activity-{len(state.activity) + 1:05d}",
            label=label,
            detail=detail,
            person_id=person_id,
            meeting_id=meeting_id,
        )
    )


def upsert_person(
    state: AppState,
    *,
    person_id: str | None = None,
    name: str,
    role: str,
    intro: str = "",
    source_url: str = "",
    topics: list[str] | None = None,
    methods: list[str] | None = None,
    projects: list[str] | None = None,
    challenges: list[str] | None = None,
    recent_updates: list[str] | None = None,
    supervisor_ids: list[str] | None = None,
    is_global_supervisor: bool | None = None,
    login_enabled: bool | None = None,
) -> Person:
    if person_id is None:
        person_id = unique_record_id(name, state.people)
        action = "Added person"
    else:
        action = "Updated person"
    person = state.people.get(person_id) or Person(id=person_id, name=name, role=role)
    person.name = name.strip()
    person.role = role.strip() or "Lab member"
    person.intro = intro.strip()
    person.source_url = source_url.strip() or "https://www.deridderlab.nl/"
    person.topics = topics or []
    person.methods = methods or []
    person.projects = [project_id for project_id in (projects or []) if project_id in state.projects]
    person.challenges = challenges or []
    person.recent_updates = recent_updates or []
    if supervisor_ids is not None:
        person.supervisor_ids = [
            supervisor_id
            for supervisor_id in dict.fromkeys(supervisor_ids)
            if supervisor_id in state.people and supervisor_id != person.id
        ]
    if is_global_supervisor is not None:
        person.is_global_supervisor = bool(is_global_supervisor)
    if person.id in GLOBAL_SUPERVISOR_IDS:
        person.is_global_supervisor = True
    if login_enabled is not None:
        person.login_enabled = bool(login_enabled)
    state.people[person.id] = person
    ensure_hierarchy_defaults(state)
    refresh_project_people(state)
    refresh_helpers(state)
    log_activity(state, action, person.name, person_id=person.id)
    return person


def action_viewer_ids(state: AppState, action_id: str) -> set[str]:
    action = state.actions.get(action_id)
    if action is None or not action.owner_id or action.owner_id not in state.people:
        return set()
    owner = state.people[action.owner_id]
    if owner.archived:
        return set()
    viewers = {owner.id}
    viewers.update(supervisor_id for supervisor_id in owner.supervisor_ids if supervisor_id in state.people and not state.people[supervisor_id].archived)
    viewers.update(person.id for person in state.people.values() if person.is_global_supervisor and not person.archived)
    return viewers


def can_view_action(state: AppState, action_id: str, viewer_id: str | None = None, *, admin: bool = False) -> bool:
    if admin:
        return True
    if not viewer_id:
        return False
    return viewer_id in action_viewer_ids(state, action_id)


def upsert_project(
    state: AppState,
    *,
    project_id: str | None = None,
    label: str,
    kind: str,
    description: str = "",
    keywords: list[str] | None = None,
    open_challenges: list[str] | None = None,
    member_ids: list[str] | None = None,
) -> ProjectTopic:
    if project_id is None:
        project_id = unique_record_id(label, state.projects)
        action = "Added group"
    else:
        action = "Updated group"
    project = state.projects.get(project_id) or ProjectTopic(id=project_id, label=label)
    project.label = label.strip()
    project.kind = kind.strip() or "theme"
    project.description = description.strip()
    project.keywords = keywords or []
    project.open_challenges = open_challenges or []
    state.projects[project.id] = project

    selected = set(member_ids or [])
    for person in state.people.values():
        if person.id in selected and project.id not in person.projects:
            person.projects.append(project.id)
        if person.id not in selected and project.id in person.projects:
            person.projects.remove(project.id)
    refresh_project_people(state)
    refresh_helpers(state)
    log_activity(state, action, project.label)
    return project


def add_member_to_project(state: AppState, project_id: str, person_id: str) -> None:
    if project_id not in state.projects or person_id not in state.people:
        raise KeyError("Unknown group or person")
    person = state.people[person_id]
    if project_id not in person.projects:
        person.projects.append(project_id)
    refresh_project_people(state)
    refresh_helpers(state)
    log_activity(state, "Added group member", f"{person.name} -> {state.projects[project_id].label}", person_id=person_id)


def remove_member_from_project(state: AppState, project_id: str, person_id: str) -> None:
    if project_id not in state.projects or person_id not in state.people:
        raise KeyError("Unknown group or person")
    person = state.people[person_id]
    if project_id in person.projects:
        person.projects.remove(project_id)
    refresh_project_people(state)
    refresh_helpers(state)
    log_activity(state, "Removed group member", f"{person.name} -> {state.projects[project_id].label}", person_id=person_id)


def set_archived(state: AppState, collection: str, item_id: str, archived: bool) -> None:
    records = getattr(state, collection)
    record = records[item_id]
    record.archived = archived
    refresh_project_people(state)
    refresh_helpers(state)
    action = "Archived" if archived else "Restored"
    label = getattr(record, "name", getattr(record, "label", getattr(record, "title", item_id)))
    log_activity(state, f"{action} {collection}", str(label))


def apply_review_decision(
    state: AppState,
    item_id: str,
    decision: ReviewStatus,
    edited_text: str | None = None,
) -> None:
    item = state.review_items[item_id]
    item.status = decision
    item.decided_at = utc_now()
    if edited_text:
        item.proposed_text = edited_text.strip()

    if decision == ReviewStatus.REJECTED:
        _mark_rejected_target(state, item)
        state.activity.append(ActivityEvent(id=f"review-{item.id}", label="Rejected draft update", detail=item.title, meeting_id=item.meeting_id))
        return

    if item.item_type == ReviewItemType.PROFILE_UPDATE:
        person_id = str(item.payload.get("person_id") or item.target_id or "")
        if person_id in state.people:
            person = state.people[person_id]
            person.topics = unique_extend(person.topics, item.payload.get("topics", []), limit=16)
            person.methods = unique_extend(person.methods, item.payload.get("methods", []), limit=12)
            person.projects = unique_extend(person.projects, item.payload.get("projects", []), limit=10)
            person.challenges = unique_extend(person.challenges, item.payload.get("challenges", []), limit=8)
            person.recent_updates = unique_extend([item.proposed_text], person.recent_updates, limit=10)
            person.last_seen_meeting_id = item.meeting_id
            state.activity.append(ActivityEvent(id=f"activity-{item.id}", label="Approved profile update", detail=item.proposed_text, person_id=person.id, meeting_id=item.meeting_id))
    elif item.item_type == ReviewItemType.ACTION_ITEM:
        action_id = str(item.payload.get("action_id", ""))
        if action_id in state.actions:
            action = state.actions[action_id]
            action.title = item.proposed_text
            action.review_status = ReviewStatus.APPROVED
            action.status = ActionStatus.OPEN
            if action.owner_id and action.owner_id in state.people:
                state.people[action.owner_id].action_ids = unique_extend(state.people[action.owner_id].action_ids, [action.id])
            state.activity.append(ActivityEvent(id=f"activity-{item.id}", label="Approved action item", detail=action.title, person_id=action.owner_id, meeting_id=action.meeting_id))
    elif item.item_type == ReviewItemType.ACTION_STATUS:
        action_id = str(item.payload.get("action_id", ""))
        proposed_status = item.payload.get("proposed_status")
        if action_id in state.actions and proposed_status:
            state.actions[action_id].status = ActionStatus(proposed_status)
            state.activity.append(ActivityEvent(id=f"activity-{item.id}", label="Updated action status", detail=item.proposed_text, meeting_id=item.meeting_id))
    elif item.item_type == ReviewItemType.LITERATURE_QUESTION:
        question_id = str(item.payload.get("question_id", ""))
        if question_id in state.literature_questions:
            question = state.literature_questions[question_id]
            question.question = item.proposed_text
            question.review_status = ReviewStatus.APPROVED
            state.activity.append(ActivityEvent(id=f"activity-{item.id}", label="Approved literature follow-up", detail=question.question, person_id=question.source_person_id, meeting_id=question.meeting_id))

    refresh_project_people(state)
    refresh_helpers(state)


def _mark_rejected_target(state: AppState, item) -> None:
    if item.item_type == ReviewItemType.ACTION_ITEM:
        action_id = str(item.payload.get("action_id", ""))
        if action_id in state.actions:
            state.actions[action_id].review_status = ReviewStatus.REJECTED
    if item.item_type == ReviewItemType.LITERATURE_QUESTION:
        question_id = str(item.payload.get("question_id", ""))
        if question_id in state.literature_questions:
            state.literature_questions[question_id].review_status = ReviewStatus.REJECTED
