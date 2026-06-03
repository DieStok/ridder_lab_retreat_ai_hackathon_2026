from __future__ import annotations

from lab_memory_atlas.auth import hash_password, verify_password
from lab_memory_atlas.models import ActionItem, LiteratureQuestion, Meeting, Person, ReviewItem, ReviewItemType, ReviewStatus
from lab_memory_atlas.pipeline import import_transcript, parse_transcript_text
from lab_memory_atlas.storage import SIG_MEMBERS, apply_review_decision, can_view_action, load_state, save_state, seed_state, slugify


SAMPLE_VTT = """WEBVTT

00:00:01.000 --> 00:00:04.000
<v Rang-3, F.J. (Franka)>We should ask Christian to run the cell typing method for the spatial transcriptomics data.</v>

00:00:05.000 --> 00:00:09.000
<v Ahmadreza>I'll compare the foundation model embeddings and read the benchmark paper.</v>

00:00:10.000 --> 00:00:13.000
<v Ahmadreza>The hard part is that the validation labels are unclear.</v>
"""


def test_parse_vtt_segments_merges_speakers() -> None:
    segments = parse_transcript_text(SAMPLE_VTT)
    assert len(segments) == 2
    assert segments[0].speaker == "Rang-3, F.J. (Franka)"
    assert "cell typing" in segments[0].text
    assert segments[1].speaker == "Ahmadreza"
    assert "benchmark paper" in segments[1].text


def test_import_transcript_creates_reviewable_lab_memory() -> None:
    state = seed_state()
    result = import_transcript(
        state,
        SAMPLE_VTT,
        source_name="demo.vtt",
        title="Spatial SIG demo",
        meeting_type="sig",
        ai_mode="heuristic",
    )

    assert result.meeting_id in state.meetings
    assert result.profile_updates_created >= 1
    assert result.actions_created >= 1
    assert result.literature_questions_created >= 1
    assert state.meetings[result.meeting_id].topic_ids
    assert any(item.status == ReviewStatus.PENDING for item in state.review_items.values())


def test_seed_state_contains_real_sig_memberships() -> None:
    state = seed_state()

    for project_id, members in SIG_MEMBERS.items():
        assert project_id in state.projects
        assert state.projects[project_id].kind == "sig"
        expected_ids = {slugify(member) for member in members}
        assert expected_ids.issubset(set(state.projects[project_id].person_ids))

    assert "jack-jiang" in state.people
    assert "sig-ml-for-omics" in state.people["jack-jiang"].projects
    assert "sig-modcall-liquidbiopsy" in state.people["jack-jiang"].projects
    assert "karol-rogozinski" in state.people
    assert "sig-ai-foundationmodels" in state.people["karol-rogozinski"].projects
    assert state.people["jeroen-de-ridder"].is_global_supervisor
    assert "paul-cozmuta" in state.people
    assert "paul" not in state.people
    assert "LeJEPA" in state.projects["foundation-models"].description
    assert "bilinear low-rank transfer head" in state.projects["foundation-models"].keywords
    assert state.projects["foundation-models"].open_challenges
    assert "LeJEPA" in state.projects["sig-ai-foundationmodels"].description


def test_approving_profile_update_changes_person_page_data() -> None:
    state = seed_state()
    import_transcript(
        state,
        SAMPLE_VTT,
        source_name="demo.vtt",
        title="Spatial SIG demo",
        meeting_type="sig",
        ai_mode="heuristic",
    )
    profile_review = next(item for item in state.review_items.values() if item.item_type == ReviewItemType.PROFILE_UPDATE)

    apply_review_decision(state, profile_review.id, ReviewStatus.APPROVED)

    person_id = str(profile_review.payload["person_id"])
    person = state.people[person_id]
    assert person.recent_updates
    assert person.last_seen_meeting_id == profile_review.meeting_id


def test_approving_action_makes_it_visible_to_owner() -> None:
    state = seed_state()
    import_transcript(
        state,
        SAMPLE_VTT,
        source_name="demo.vtt",
        title="Spatial SIG demo",
        meeting_type="sig",
        ai_mode="heuristic",
    )
    action_review = next(item for item in state.review_items.values() if item.item_type == ReviewItemType.ACTION_ITEM)

    apply_review_decision(state, action_review.id, ReviewStatus.APPROVED)

    action_id = str(action_review.payload["action_id"])
    action = state.actions[action_id]
    assert action.review_status == ReviewStatus.APPROVED
    if action.owner_id:
        assert action_id in state.people[action.owner_id].action_ids


def test_password_hashes_and_private_action_viewers() -> None:
    state = seed_state()
    state.people["ahmadreza-iranpour"].supervisor_ids = ["franka-rang"]
    state.actions["private-action"] = ActionItem(
        id="private-action",
        owner_id="ahmadreza-iranpour",
        title="Compare embeddings",
        meeting_id="manual",
        review_status=ReviewStatus.APPROVED,
    )

    encoded = hash_password("member-pin")

    assert encoded != "member-pin"
    assert verify_password("member-pin", encoded)
    assert not verify_password("wrong", encoded)
    assert can_view_action(state, "private-action", "ahmadreza-iranpour")
    assert can_view_action(state, "private-action", "franka-rang")
    assert can_view_action(state, "private-action", "jeroen-de-ridder")
    assert not can_view_action(state, "private-action", "carlos-garcia-fernandez")
    assert not can_view_action(state, "private-action", None)


def test_load_state_merges_paul_into_paul_cozmuta(tmp_path) -> None:
    state = seed_state()
    state.seed_version = 2
    state.people["paul"] = Person(
        id="paul",
        name="Paul",
        role="Meeting participant",
        topics=["cell typing"],
        projects=["spatial-transcriptomics"],
        action_ids=["action-paul"],
    )
    state.meetings["meeting-paul"] = Meeting(id="meeting-paul", title="Paul meeting", speaker_ids=["paul"])
    state.actions["action-paul"] = ActionItem(
        id="action-paul",
        owner_id="paul",
        title="Check clustering outputs",
        meeting_id="meeting-paul",
        review_status=ReviewStatus.APPROVED,
    )
    state.literature_questions["lit-paul"] = LiteratureQuestion(
        id="lit-paul",
        question="Check the paper",
        source_person_id="paul",
        meeting_id="meeting-paul",
    )
    state.review_items["review-paul"] = ReviewItem(
        id="review-paul",
        item_type=ReviewItemType.PROFILE_UPDATE,
        title="Update Paul's profile",
        proposed_text="Discussed clustering.",
        payload={"person_id": "paul", "nested": ["paul"]},
        target_id="paul",
    )
    save_state(state, tmp_path)

    migrated = load_state(tmp_path)

    assert migrated.seed_version == 4
    assert "paul" not in migrated.people
    assert "paul-cozmuta" in migrated.people
    assert "cell typing" in migrated.people["paul-cozmuta"].topics
    assert "action-paul" in migrated.people["paul-cozmuta"].action_ids
    assert migrated.meetings["meeting-paul"].speaker_ids == ["paul-cozmuta"]
    assert migrated.actions["action-paul"].owner_id == "paul-cozmuta"
    assert migrated.literature_questions["lit-paul"].source_person_id == "paul-cozmuta"
    assert migrated.review_items["review-paul"].target_id == "paul-cozmuta"
    assert migrated.review_items["review-paul"].payload["person_id"] == "paul-cozmuta"
    assert migrated.review_items["review-paul"].payload["nested"] == ["paul-cozmuta"]
