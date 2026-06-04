from __future__ import annotations

import json
import os
import re
import uuid
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

from .models import (
    ActionItem,
    ActionStatus,
    AppState,
    LiteratureQuestion,
    Meeting,
    MeetingType,
    Person,
    ReviewItem,
    ReviewItemType,
)
from .storage import slugify


STOPWORDS = {
    "about", "after", "again", "actually", "also", "and", "are", "because", "been", "but",
    "can", "could", "did", "does", "doing", "for", "from", "get", "go", "going", "good",
    "great", "had", "has", "have", "how", "into", "just", "like", "make", "maybe", "more",
    "nice", "not", "now", "okay", "our", "out", "that", "the", "then", "there", "this",
    "right", "see", "sure", "think", "was", "we", "yeah", "yes", "what", "when", "with",
    "would", "you", "your", "they", "them", "very", "some", "one",
}

ACTION_RE = re.compile(
    r"\b(action|todo|follow up|need to|needs to|should|we will|i will|i'll|let's|"
    r"send|prepare|check|ask|write|create|run|compare|try|book|email|look up|read)\b",
    re.IGNORECASE,
)
DECISION_RE = re.compile(r"\b(decided|decision|we will|we should|let's|plan is|agreed|going to)\b", re.IGNORECASE)
BLOCKED_RE = re.compile(r"\b(blocked|stuck|cannot|can't|waiting|problem|issue|failed|not working|unclear)\b", re.IGNORECASE)
DONE_RE = re.compile(r"\b(done|finished|completed|sent|submitted|uploaded|fixed|resolved|worked)\b", re.IGNORECASE)
CHALLENGE_RE = re.compile(r"\b(challenge|problem|issue|blocked|stuck|hard|difficult|unclear|not working|failed|risk)\b", re.IGNORECASE)
LITERATURE_RE = re.compile(
    r"\b(paper|literature|pubmed|arxiv|read|review|method|benchmark|dataset|model|"
    r"methylation|foundation|spatial|transcriptomics|single-cell|single cell|proteomics)\b",
    re.IGNORECASE,
)


@dataclass
class Segment:
    speaker: str
    text: str
    timestamp: str = ""


@dataclass
class ImportResult:
    meeting_id: str
    review_items_created: int
    actions_created: int
    literature_questions_created: int
    profile_updates_created: int


def clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_transcript_file(path: Path) -> list[Segment]:
    return parse_transcript_text(path.read_text(encoding="utf-8", errors="replace"))


def parse_transcript_text(raw: str) -> list[Segment]:
    if raw.lstrip().startswith("WEBVTT"):
        return parse_vtt(raw)
    return parse_plain_text(raw)


def parse_vtt(raw: str) -> list[Segment]:
    segments: list[Segment] = []
    current_timestamp = ""
    text_lines: list[str] = []

    for line in raw.splitlines():
        line = line.strip()
        if not line or line == "WEBVTT":
            if text_lines:
                segments.extend(segments_from_block(text_lines, current_timestamp))
                text_lines = []
            current_timestamp = ""
            continue
        if "-->" in line:
            current_timestamp = line
            continue
        if re.match(r"^[\w-]+/\d+-\d+$", line):
            continue
        text_lines.append(line)

    if text_lines:
        segments.extend(segments_from_block(text_lines, current_timestamp))
    return merge_adjacent_segments(segments)


def segments_from_block(lines: list[str], timestamp: str) -> list[Segment]:
    raw_block = " ".join(lines)
    speaker_match = re.search(r"<v\s+([^>]+)>(.*?)</v>", raw_block, re.DOTALL)
    if speaker_match:
        speaker = clean_text(speaker_match.group(1))
        text = clean_text(speaker_match.group(2))
    else:
        speaker = "Unknown"
        text = clean_text(raw_block)
    return [Segment(speaker=speaker, text=text, timestamp=timestamp)] if text else []


def parse_plain_text(raw: str) -> list[Segment]:
    segments: list[Segment] = []
    for line in raw.splitlines():
        line = clean_text(line)
        if not line:
            continue
        speaker_match = re.match(r"^([^:]{1,80}):\s+(.+)$", line)
        if speaker_match:
            segments.append(Segment(speaker=speaker_match.group(1).strip(), text=speaker_match.group(2).strip()))
        else:
            segments.append(Segment(speaker="Unknown", text=line))
    return merge_adjacent_segments(segments)


def merge_adjacent_segments(segments: list[Segment]) -> list[Segment]:
    merged: list[Segment] = []
    for segment in segments:
        if merged and merged[-1].speaker == segment.speaker:
            merged[-1].text = f"{merged[-1].text} {segment.text}"
        else:
            merged.append(segment)
    return merged


def sentence_split(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [part.strip(" -") for part in parts if len(part.strip()) > 8]


def keywords(text: str, limit: int = 10) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text.lower())
    counts: dict[str, int] = {}
    for word in words:
        if word in STOPWORDS:
            continue
        counts[word] = counts.get(word, 0) + 1
    return [word for word, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]]


def import_transcript(
    state: AppState,
    raw_text: str,
    source_name: str,
    title: str,
    meeting_type: str = MeetingType.LAB_MEETING.value,
    meeting_date: date | None = None,
    sensitive: bool = False,
    ai_mode: str | None = None,
) -> ImportResult:
    segments = parse_transcript_text(raw_text)
    if not segments:
        raise ValueError("No usable transcript segments found.")

    meeting_id = next_id("meeting", title, state.meetings)
    speaker_ids = ensure_speakers(state, segments)
    topic_ids = detect_topic_ids(state, " ".join(segment.text for segment in segments))
    summary = maybe_ai_summary(raw_text, ai_mode) or summarize_meeting(segments)

    meeting = Meeting(
        id=meeting_id,
        title=title.strip() or source_name or "Imported meeting",
        meeting_type=safe_meeting_type(meeting_type),
        meeting_date=meeting_date,
        source_name=source_name,
        sensitive=sensitive or meeting_type == MeetingType.ONE_ON_ONE.value,
        summary=summary,
        decisions=choose_sentences(segments, DECISION_RE, 8),
        open_questions=extract_open_questions(segments, 8),
        speaker_ids=speaker_ids,
        topic_ids=topic_ids,
    )
    state.meetings[meeting.id] = meeting

    profile_count = create_profile_update_reviews(state, meeting, segments)
    action_count = create_action_reviews(state, meeting, segments)
    literature_count = create_literature_reviews(state, meeting, segments)
    create_action_status_reviews(state, meeting, segments)

    return ImportResult(
        meeting_id=meeting.id,
        review_items_created=sum(1 for item in state.review_items.values() if item.meeting_id == meeting.id),
        actions_created=action_count,
        literature_questions_created=literature_count,
        profile_updates_created=profile_count,
    )


def next_id(prefix: str, label: str, existing: dict[str, object]) -> str:
    base = slugify(label)[:36] or prefix
    candidate = f"{prefix}-{base}"
    if candidate not in existing:
        return candidate
    return f"{candidate}-{uuid.uuid4().hex[:6]}"


def safe_meeting_type(value: str) -> MeetingType:
    try:
        return MeetingType(value)
    except ValueError:
        return MeetingType.OTHER


def ensure_speakers(state: AppState, segments: list[Segment]) -> list[str]:
    speaker_ids: list[str] = []
    for speaker in sorted({segment.speaker for segment in segments}):
        person_id = match_person_id(state, speaker)
        if not person_id:
            person_id = slugify(speaker)
            state.people[person_id] = Person(
                id=person_id,
                name=speaker,
                role="Meeting participant",
                intro="Added from a transcript. Approve meeting-derived updates to build this profile.",
            )
        if person_id not in speaker_ids:
            speaker_ids.append(person_id)
    return speaker_ids


def match_person_id(state: AppState, speaker: str) -> str | None:
    normalized = speaker.lower()
    normalized = re.sub(r"rang-3,\s*f\.j\.\s*\(([^)]+)\)", r"\1", normalized)
    normalized = re.sub(r"[^a-z0-9 ]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    for person in state.people.values():
        person_name = person.name.lower()
        first = person_name.split()[0]
        if normalized == person_name or normalized == first or first in normalized:
            return person.id
    return None


def detect_topic_ids(state: AppState, text: str) -> list[str]:
    lowered = text.lower()
    matched: list[str] = []
    for topic in state.projects.values():
        if any(keyword.lower() in lowered for keyword in topic.keywords + [topic.label]):
            matched.append(topic.id)
    return matched[:8]


def summarize_meeting(segments: list[Segment]) -> str:
    sentences = sentence_split(" ".join(segment.text for segment in segments))
    if not sentences:
        return "No usable transcript content found."
    ranked = sorted(sentences, key=lambda sentence: len(set(keywords(sentence, limit=12))), reverse=True)
    summary = ranked[0]
    return summary[:320]


def maybe_ai_summary(raw_text: str, ai_mode: str | None = None) -> str | None:
    mode = (ai_mode or os.getenv("LAB_ATLAS_AI_MODE", "heuristic")).lower()
    if mode == "heuristic":
        return None
    if mode in {"hybrid", "ollama"}:
        summary = try_ollama_summary(raw_text)
        if summary or mode == "ollama":
            return summary
    if mode in {"hybrid", "cloud", "litellm"}:
        return try_cloud_summary(raw_text)
    return None


def try_ollama_summary(raw_text: str) -> str | None:
    try:
        import httpx

        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        model = os.getenv("LAB_ATLAS_OLLAMA_MODEL", "llama3.2")
        prompt = (
            "Summarize this lab meeting transcript in one precise sentence for an internal people/project atlas. "
            "Mention project context and follow-up direction when present. Transcript:\n\n"
            f"{raw_text[:6000]}"
        )
        response = httpx.post(
            f"{base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=2.5,
        )
        if response.status_code >= 400:
            return None
        text = str(response.json().get("response", "")).strip()
        return text[:420] or None
    except Exception:
        return None


def try_cloud_summary(raw_text: str) -> str | None:
    model = os.getenv("LAB_ATLAS_CLOUD_MODEL")
    if not model:
        return None
    try:
        import litellm

        response = litellm.completion(
            model=model,
            messages=[
                {"role": "system", "content": "Return one precise sentence for an internal lab meeting atlas."},
                {"role": "user", "content": raw_text[:6000]},
            ],
            timeout=8,
        )
        return response.choices[0].message.content.strip()[:420]
    except Exception:
        return None


def choose_sentences(segments: list[Segment], pattern: re.Pattern[str], limit: int) -> list[str]:
    picked: list[str] = []
    seen: set[str] = set()
    for segment in segments:
        for sentence in sentence_split(segment.text):
            normalized = re.sub(r"\W+", " ", sentence.lower()).strip()
            if normalized in seen or not pattern.search(sentence):
                continue
            picked.append(f"{segment.speaker}: {sentence}")
            seen.add(normalized)
            if len(picked) >= limit:
                return picked
    return picked


def extract_open_questions(segments: list[Segment], limit: int) -> list[str]:
    questions: list[str] = []
    for segment in segments:
        for sentence in sentence_split(segment.text):
            if "?" in sentence or re.search(r"\b(unclear|question|wonder|whether|how do we|what if)\b", sentence, re.IGNORECASE):
                questions.append(f"{segment.speaker}: {sentence}")
                if len(questions) >= limit:
                    return questions
    return questions


def create_profile_update_reviews(state: AppState, meeting: Meeting, segments: list[Segment]) -> int:
    by_person: dict[str, list[str]] = {}
    for segment in segments:
        person_id = match_person_id(state, segment.speaker)
        if person_id:
            by_person.setdefault(person_id, []).append(segment.text)

    created = 0
    for person_id, texts in by_person.items():
        combined = " ".join(texts)
        topic_ids = detect_topic_ids(state, combined)
        topic_labels = [state.projects[topic_id].label for topic_id in topic_ids if topic_id in state.projects]
        contribution = best_contribution_sentence(combined)
        challenges = challenge_sentences(combined, limit=3)
        if not contribution and not topic_labels and not challenges:
            continue
        review_id = f"review-profile-{meeting.id}-{person_id}"
        state.review_items[review_id] = ReviewItem(
            id=review_id,
            item_type=ReviewItemType.PROFILE_UPDATE,
            title=f"Update {state.people[person_id].name}'s profile",
            proposed_text=contribution or f"Discussed {', '.join(topic_labels[:3])}.",
            payload={
                "person_id": person_id,
                "topics": topic_labels + keywords(combined, limit=5),
                "methods": method_terms(combined),
                "projects": topic_ids,
                "challenges": challenges,
            },
            meeting_id=meeting.id,
            target_id=person_id,
            evidence=combined[:500],
            sensitive=meeting.sensitive,
        )
        created += 1
    return created


def best_contribution_sentence(text: str) -> str:
    sentences = sentence_split(text)
    if not sentences:
        return ""
    signals = [sentence for sentence in sentences if DECISION_RE.search(sentence) or LITERATURE_RE.search(sentence) or CHALLENGE_RE.search(sentence)]
    candidate = (signals or sentences)[0]
    return candidate[:280]


def challenge_sentences(text: str, limit: int) -> list[str]:
    return [sentence[:260] for sentence in sentence_split(text) if CHALLENGE_RE.search(sentence)][:limit]


def method_terms(text: str) -> list[str]:
    known = [
        "nanopore", "methylation", "spatial transcriptomics", "single-cell", "proteomics",
        "foundation models", "image embeddings", "classification", "cell typing", "HPC",
        "multi-omics", "3D genome", "cfDNA",
    ]
    lowered = text.lower()
    return [term for term in known if term.lower() in lowered]


def create_action_reviews(state: AppState, meeting: Meeting, segments: list[Segment]) -> int:
    created = 0
    seen: set[str] = set()
    for segment in segments:
        owner_id = match_person_id(state, segment.speaker)
        for sentence in sentence_split(segment.text):
            if not ACTION_RE.search(sentence) or is_weak_action_candidate(sentence):
                continue
            normalized = re.sub(r"\W+", " ", sentence.lower()).strip()
            if normalized in seen:
                continue
            seen.add(normalized)
            action_id = f"action-{meeting.id}-{created + 1:03d}"
            importance, effort, uncertainty, risk_reward = score_work_item(sentence)
            action = ActionItem(
                id=action_id,
                owner_id=owner_id,
                title=sentence[:280],
                context=f"Extracted from {meeting.title}",
                meeting_id=meeting.id,
                evidence=f"{segment.speaker}: {sentence}",
                importance=importance,
                estimated_time=effort,
                uncertainty=uncertainty,
                risk_reward=risk_reward,
                priority_score=priority_score(importance, effort, uncertainty, risk_reward),
            )
            state.actions[action.id] = action
            review_id = f"review-action-{action.id}"
            state.review_items[review_id] = ReviewItem(
                id=review_id,
                item_type=ReviewItemType.ACTION_ITEM,
                title="Review action item",
                proposed_text=action.title,
                payload={"action_id": action.id},
                meeting_id=meeting.id,
                target_id=action.owner_id,
                evidence=action.evidence,
                sensitive=meeting.sensitive,
            )
            created += 1
            if created >= 12:
                return created
    return created


def is_weak_action_candidate(sentence: str) -> bool:
    lowered = sentence.lower()
    weak_fragments = [
        "can you see",
        "how can we",
        "i don't know",
        "i will show you",
        "i will mention it",
        "when you ask",
        "would for sure not try",
        "maybe i will just share my screen",
    ]
    return lowered.endswith("?") or any(fragment in lowered for fragment in weak_fragments)


def create_literature_reviews(state: AppState, meeting: Meeting, segments: list[Segment]) -> int:
    created = 0
    seen: set[str] = set()
    for segment in segments:
        source_person_id = match_person_id(state, segment.speaker)
        for sentence in sentence_split(segment.text):
            if not LITERATURE_RE.search(sentence):
                continue
            query_terms = keywords(sentence, limit=6)
            if not query_terms:
                continue
            search_prompt = " ".join(query_terms[:5])
            if search_prompt in seen:
                continue
            seen.add(search_prompt)
            question_id = f"lit-{meeting.id}-{created + 1:03d}"
            importance, effort, uncertainty, risk_reward = score_work_item(sentence)
            question = LiteratureQuestion(
                id=question_id,
                question=sentence[:320],
                search_prompt=search_prompt,
                source_person_id=source_person_id,
                meeting_id=meeting.id,
                evidence=f"{segment.speaker}: {sentence}",
                importance=importance,
                estimated_time=effort,
                uncertainty=uncertainty,
                risk_reward=risk_reward,
                priority_score=priority_score(importance, effort, uncertainty, risk_reward),
            )
            state.literature_questions[question.id] = question
            review_id = f"review-lit-{question.id}"
            state.review_items[review_id] = ReviewItem(
                id=review_id,
                item_type=ReviewItemType.LITERATURE_QUESTION,
                title="Review literature follow-up",
                proposed_text=question.question,
                payload={"question_id": question.id},
                meeting_id=meeting.id,
                target_id=source_person_id,
                evidence=question.evidence,
                sensitive=meeting.sensitive,
            )
            created += 1
            if created >= 10:
                return created
    return created


def score_work_item(text: str) -> tuple[int, int, int, int]:
    lowered = text.lower()
    importance = 3
    if any(term in lowered for term in ["decision", "need", "should", "after this meeting", "blocked", "failed"]):
        importance += 1
    if any(term in lowered for term in ["diagnostic", "patient", "clinical", "foundation", "spatial", "methylation"]):
        importance += 1
    effort = 2 if len(text) < 120 else 3
    if any(term in lowered for term in ["build", "implement", "benchmark", "compare", "review"]):
        effort += 1
    uncertainty = 4 if CHALLENGE_RE.search(text) else 2
    risk_reward = max(1, min(5, importance + uncertainty - effort))
    return min(5, importance), min(5, effort), min(5, uncertainty), risk_reward


def priority_score(importance: int, effort: int, uncertainty: int, risk_reward: int) -> int:
    return (importance * 3) + (risk_reward * 2) + uncertainty - effort


def create_action_status_reviews(state: AppState, meeting: Meeting, segments: list[Segment]) -> int:
    full_text_lower = " ".join(segment.text for segment in segments).lower()
    created = 0
    for action in state.approved_actions():
        if action.status in {ActionStatus.DONE}:
            continue
        terms = [term for term in keywords(action.title, limit=8) if len(term) > 3]
        overlap = [term for term in terms if term in full_text_lower]
        if len(overlap) < 2:
            continue
        evidence = find_evidence_sentence(segments, overlap)
        proposed = ActionStatus.UNCLEAR
        if evidence and DONE_RE.search(evidence):
            proposed = ActionStatus.LIKELY_DONE
        elif evidence and BLOCKED_RE.search(evidence):
            proposed = ActionStatus.BLOCKED
        review_id = f"review-status-{meeting.id}-{action.id}"
        state.review_items[review_id] = ReviewItem(
            id=review_id,
            item_type=ReviewItemType.ACTION_STATUS,
            title="Review action status",
            proposed_text=f"{action.title} -> {proposed.value}",
            payload={"action_id": action.id, "proposed_status": proposed.value},
            meeting_id=meeting.id,
            target_id=action.owner_id,
            evidence=evidence or "Topic appeared again, but completion evidence was unclear.",
            sensitive=meeting.sensitive,
        )
        created += 1
    return created


def find_evidence_sentence(segments: list[Segment], terms: Iterable[str]) -> str:
    terms = [term.lower() for term in terms]
    for segment in segments:
        for sentence in sentence_split(segment.text):
            sentence_lower = sentence.lower()
            if any(term in sentence_lower for term in terms):
                return f"{segment.speaker}: {sentence}"
    return ""


def export_state_snapshot(state: AppState, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "people": [person.model_dump(mode="json") for person in state.people.values()],
        "projects": [project.model_dump(mode="json") for project in state.projects.values()],
        "meetings": [meeting.model_dump(mode="json") for meeting in state.meetings.values()],
        "actions": [action.model_dump(mode="json") for action in state.actions.values()],
        "literature_questions": [question.model_dump(mode="json") for question in state.literature_questions.values()],
    }
    path = output_dir / "lab_memory_snapshot.json"
    path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    return path
