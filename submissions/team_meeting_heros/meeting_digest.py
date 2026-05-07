#!/usr/bin/env python3
"""Transcript-first meeting memory prototype for team_meeting_heros."""

from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


STOPWORDS = {
    "about",
    "after",
    "again",
    "actually",
    "also",
    "and",
    "are",
    "because",
    "been",
    "but",
    "can",
    "could",
    "did",
    "does",
    "doing",
    "for",
    "from",
    "get",
    "go",
    "going",
    "good",
    "great",
    "had",
    "has",
    "have",
    "how",
    "into",
    "just",
    "like",
    "make",
    "maybe",
    "mhm",
    "more",
    "nice",
    "not",
    "now",
    "okay",
    "our",
    "out",
    "that",
    "the",
    "then",
    "there",
    "this",
    "right",
    "see",
    "sure",
    "think",
    "was",
    "we",
    "yeah",
    "yes",
    "what",
    "when",
    "with",
    "would",
    "you",
    "your",
}

ACTION_RE = re.compile(
    r"\b("
    r"action|todo|follow up|need to|needs to|should|we will|i will|i'll|"
    r"let's|can we|could we|send|prepare|check|ask|write|create|run|"
    r"compare|try to|book|email|look up|read"
    r")\b",
    re.IGNORECASE,
)
DECISION_RE = re.compile(
    r"\b(decided|decision|we will|we should|let's|plan is|going to|agreed)\b",
    re.IGNORECASE,
)
BLOCKED_RE = re.compile(r"\b(blocked|stuck|cannot|can't|waiting|problem|issue|failed|not working)\b", re.IGNORECASE)
DONE_RE = re.compile(r"\b(done|finished|completed|sent|submitted|uploaded|fixed|resolved|worked)\b", re.IGNORECASE)
LITERATURE_RE = re.compile(
    r"\b(paper|literature|pubmed|arxiv|read|review|method|benchmark|dataset|model|"
    r"methylation|foundation|spatial|transcriptomics|single-cell|single cell)\b",
    re.IGNORECASE,
)


@dataclass
class Segment:
    speaker: str
    text: str
    timestamp: str = ""


def clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_transcript(path: Path) -> list[Segment]:
    raw = path.read_text(encoding="utf-8", errors="replace")
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
    block = clean_text(" ".join(lines))
    if not block:
        return []
    speaker_match = re.search(r"<v\s+([^>]+)>(.*?)</v>", " ".join(lines), re.DOTALL)
    if speaker_match:
        speaker = clean_text(speaker_match.group(1))
        text = clean_text(speaker_match.group(2))
    else:
        speaker = "Unknown"
        text = block
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
    counts = Counter(word for word in words if word not in STOPWORDS)
    return [word for word, _ in counts.most_common(limit)]


def choose_snippets(segments: list[Segment], pattern: re.Pattern[str], limit: int) -> list[dict[str, str]]:
    snippets: list[dict[str, str]] = []
    for segment in segments:
        for sentence in sentence_split(segment.text):
            if pattern.search(sentence):
                snippets.append({"speaker": segment.speaker, "text": sentence, "timestamp": segment.timestamp})
                if len(snippets) >= limit:
                    return snippets
    return snippets


def build_actions(segments: list[Segment]) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    seen: set[str] = set()
    for segment in segments:
        for sentence in sentence_split(segment.text):
            if not ACTION_RE.search(sentence):
                continue
            if is_weak_action_candidate(sentence):
                continue
            normalized = re.sub(r"\W+", " ", sentence.lower()).strip()
            if normalized in seen:
                continue
            seen.add(normalized)
            actions.append(
                {
                    "id": f"A{len(actions) + 1:03d}",
                    "owner": segment.speaker,
                    "task": sentence,
                    "status": "new",
                    "evidence": segment.timestamp or segment.speaker,
                    "review_note": "Needs human approval before becoming the official action list.",
                }
            )
    return actions[:12]


def is_weak_action_candidate(sentence: str) -> bool:
    lowered = sentence.lower()
    if lowered.endswith("?"):
        return True
    weak_fragments = [
        "can you see",
        "how can we",
        "i don't know",
        "i will show you",
        "i will mention it",
        "when you ask",
        "would for sure not try",
    ]
    return any(fragment in lowered for fragment in weak_fragments)


def assess_previous_actions(previous_memory: Path | None, segments: list[Segment]) -> list[dict[str, str]]:
    if not previous_memory:
        return []
    data = json.loads(previous_memory.read_text(encoding="utf-8"))
    prior_actions = data.get("actions", [])
    full_text = " ".join(segment.text for segment in segments)
    full_text_lower = full_text.lower()
    assessments: list[dict[str, str]] = []

    for action in prior_actions:
        task = str(action.get("task", ""))
        action_terms = [term for term in keywords(task, limit=8) if len(term) > 3]
        overlap = [term for term in action_terms if term in full_text_lower]
        evidence = find_evidence_sentence(segments, overlap)
        status = "unknown"
        if evidence and DONE_RE.search(evidence):
            status = "likely_done"
        elif evidence and BLOCKED_RE.search(evidence):
            status = "blocked"
        elif len(overlap) >= 2:
            status = "discussed_again"
        assessments.append(
            {
                "id": str(action.get("id", "")),
                "task": task,
                "previous_owner": str(action.get("owner", "")),
                "proposed_status": status,
                "evidence": evidence or "No clear evidence found in this transcript.",
                "review_note": "Human review required before sharing.",
            }
        )
    return assessments


def find_evidence_sentence(segments: list[Segment], terms: Iterable[str]) -> str:
    terms = [term.lower() for term in terms]
    for segment in segments:
        for sentence in sentence_split(segment.text):
            sentence_lower = sentence.lower()
            if any(term in sentence_lower for term in terms):
                return f"{segment.speaker}: {sentence}"
    return ""


def build_literature_ideas(segments: list[Segment]) -> list[dict[str, str | int]]:
    ideas: list[dict[str, str | int]] = []
    seen: set[str] = set()
    for segment in segments:
        for sentence in sentence_split(segment.text):
            if not LITERATURE_RE.search(sentence):
                continue
            terms = keywords(sentence, limit=6)
            if not terms:
                continue
            query = " ".join(terms[:5])
            if query in seen:
                continue
            seen.add(query)
            importance = min(5, 2 + sum(1 for term in terms if term in {"model", "dataset", "benchmark", "methylation", "spatial", "transcriptomics"}))
            effort = 2 if len(sentence) < 120 else 3
            reward = max(1, importance - effort + 3)
            ideas.append(
                {
                    "question": sentence,
                    "search_query": query,
                    "importance": importance,
                    "estimated_effort": effort,
                    "risk_reward_score": reward,
                    "source": segment.speaker,
                }
            )
    return sorted(ideas, key=lambda item: (-int(item["risk_reward_score"]), -int(item["importance"])))[:8]


def person_profiles(segments: list[Segment], actions: list[dict[str, str]]) -> dict[str, dict[str, object]]:
    profiles: dict[str, dict[str, object]] = {}
    by_speaker: dict[str, list[str]] = defaultdict(list)
    for segment in segments:
        by_speaker[segment.speaker].append(segment.text)

    for speaker, texts in by_speaker.items():
        combined = " ".join(texts)
        profiles[speaker] = {
            "speaker": speaker,
            "topics": keywords(combined, limit=8),
            "recent_contributions": [snippet["text"] for snippet in choose_snippets([Segment(speaker, combined)], DECISION_RE, 3)],
            "open_actions": [action for action in actions if action["owner"] == speaker],
            "suggested_helpers": [],
        }

    shared_topics = {speaker: set(profile["topics"]) for speaker, profile in profiles.items()}
    for speaker, profile in profiles.items():
        helper_scores = []
        for other, other_topics in shared_topics.items():
            if other == speaker:
                continue
            overlap = sorted(set(profile["topics"]) & other_topics)
            if overlap:
                helper_scores.append((len(overlap), other, overlap))
        profile["suggested_helpers"] = [
            {"person": other, "shared_topics": overlap}
            for _, other, overlap in sorted(helper_scores, reverse=True)[:3]
        ]
    return profiles


def build_memory(args: argparse.Namespace, segments: list[Segment]) -> dict[str, object]:
    full_text = " ".join(segment.text for segment in segments)
    actions = build_actions(segments)
    memory = {
        "team": "meeting_heros",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "meeting_title": args.meeting_title,
        "meeting_type": args.meeting_type,
        "input_file": str(args.transcript),
        "speakers": sorted({segment.speaker for segment in segments}),
        "summary": {
            "one_sentence": summarize_one_sentence(full_text),
            "top_topics": keywords(full_text, limit=12),
            "decisions": choose_snippets(segments, DECISION_RE, 8),
            "open_questions": extract_open_questions(segments),
        },
        "actions": actions,
        "previous_action_assessments": assess_previous_actions(args.previous_memory, segments),
        "literature_followups": build_literature_ideas(segments),
    }
    memory["people"] = person_profiles(segments, actions)
    return memory


def summarize_one_sentence(text: str) -> str:
    sentences = sentence_split(text)
    if not sentences:
        return "No usable transcript content found."
    ranked = sorted(sentences, key=lambda sentence: len(set(keywords(sentence, limit=10))), reverse=True)
    return ranked[0][:260]


def extract_open_questions(segments: list[Segment]) -> list[dict[str, str]]:
    questions = []
    for segment in segments:
        for sentence in sentence_split(segment.text):
            if "?" in sentence or re.search(r"\b(unclear|question|wonder|whether|how do we|what if)\b", sentence, re.IGNORECASE):
                questions.append({"speaker": segment.speaker, "text": sentence, "timestamp": segment.timestamp})
                if len(questions) >= 8:
                    return questions
    return questions


def write_outputs(memory: dict[str, object], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "people").mkdir(exist_ok=True)
    (output / "meeting_memory.json").write_text(json.dumps(memory, indent=2), encoding="utf-8")
    (output / "meeting_digest.md").write_text(render_digest(memory), encoding="utf-8")
    (output / "slack_summary.md").write_text(render_slack(memory), encoding="utf-8")
    (output / "index.html").write_text(render_index(memory), encoding="utf-8")

    people = memory.get("people", {})
    if isinstance(people, dict):
        for speaker, profile in people.items():
            slug = slugify(str(speaker))
            (output / "people" / f"{slug}.html").write_text(render_person_page(profile), encoding="utf-8")


def render_digest(memory: dict[str, object]) -> str:
    summary = memory["summary"]
    assert isinstance(summary, dict)
    lines = [
        f"# {memory['meeting_title']} - Meeting Digest",
        "",
        f"Type: `{memory['meeting_type']}`",
        f"Generated by: `meeting_heros`",
        "",
        "## Short summary",
        "",
        str(summary["one_sentence"]),
        "",
        "## Top topics",
        "",
        bullet_list(summary.get("top_topics", [])),
        "",
        "## Decisions and strong signals",
        "",
        snippet_list(summary.get("decisions", [])),
        "",
        "## Action points",
        "",
        action_list(memory.get("actions", [])),
        "",
        "## Previous action assessment",
        "",
        previous_action_list(memory.get("previous_action_assessments", [])),
        "",
        "## Literature follow-up ideas",
        "",
        literature_list(memory.get("literature_followups", [])),
        "",
        "## Open questions",
        "",
        snippet_list(summary.get("open_questions", [])),
        "",
        "## Speakers",
        "",
        bullet_list(memory.get("speakers", [])),
    ]
    return "\n".join(lines)


def render_slack(memory: dict[str, object]) -> str:
    summary = memory["summary"]
    assert isinstance(summary, dict)
    actions = memory.get("actions", [])
    literature = memory.get("literature_followups", [])
    lines = [
        f"*{memory['meeting_title']} - lab update*",
        "",
        str(summary["one_sentence"]),
        "",
        "*Top topics:* " + ", ".join(summary.get("top_topics", [])[:6]),
        "",
        "*Action points to review:*",
        compact_action_list(actions, limit=5),
        "",
        "*Suggested literature follow-up:*",
        compact_literature_list(literature, limit=3),
        "",
        "_Draft generated by meeting_heros. Please review before sharing broadly._",
    ]
    return "\n".join(lines)


def render_index(memory: dict[str, object]) -> str:
    people = memory.get("people", {})
    people_links = ""
    if isinstance(people, dict):
        people_links = "\n".join(
            f'<li><a href="people/{slugify(str(name))}.html">{html.escape(str(name))}</a></li>'
            for name in sorted(people)
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(str(memory['meeting_title']))} - meeting_heros</title>
  <style>{css()}</style>
</head>
<body>
  <main>
    <p class="eyebrow">meeting_heros</p>
    <h1>{html.escape(str(memory['meeting_title']))}</h1>
    <p>{html.escape(str(memory['summary']['one_sentence']))}</p>
    <section>
      <h2>Outputs</h2>
      <ul>
        <li><a href="meeting_digest.md">Meeting digest</a></li>
        <li><a href="slack_summary.md">Slack-ready summary</a></li>
        <li><a href="meeting_memory.json">Structured meeting memory</a></li>
      </ul>
    </section>
    <section>
      <h2>People</h2>
      <ul>{people_links}</ul>
    </section>
  </main>
</body>
</html>
"""


def render_person_page(profile: object) -> str:
    assert isinstance(profile, dict)
    actions = profile.get("open_actions", [])
    helpers = profile.get("suggested_helpers", [])
    helper_items = ""
    if isinstance(helpers, list):
        helper_items = "\n".join(
            f"<li>{html.escape(str(item.get('person', '')))} - shared topics: {html.escape(', '.join(item.get('shared_topics', [])))}</li>"
            for item in helpers
            if isinstance(item, dict)
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(str(profile['speaker']))} - collaboration profile</title>
  <style>{css()}</style>
</head>
<body>
  <main>
    <p class="eyebrow">collaboration profile</p>
    <h1>{html.escape(str(profile['speaker']))}</h1>
    <section>
      <h2>Current topics</h2>
      <p>{html.escape(', '.join(profile.get('topics', [])))}</p>
    </section>
    <section>
      <h2>Recent contributions</h2>
      <ul>{html_list(profile.get('recent_contributions', []))}</ul>
    </section>
    <section>
      <h2>Open action points</h2>
      <ul>{html_action_list(actions)}</ul>
    </section>
    <section>
      <h2>Suggested helpers</h2>
      <ul>{helper_items or '<li>No strong topic overlap found yet.</li>'}</ul>
    </section>
  </main>
</body>
</html>
"""


def bullet_list(items: object) -> str:
    if not isinstance(items, list) or not items:
        return "- None detected."
    return "\n".join(f"- {item}" for item in items)


def snippet_list(items: object) -> str:
    if not isinstance(items, list) or not items:
        return "- None detected."
    lines = []
    for item in items:
        if isinstance(item, dict):
            lines.append(f"- **{item.get('speaker', 'Unknown')}**: {item.get('text', '')}")
    return "\n".join(lines) if lines else "- None detected."


def action_list(items: object) -> str:
    if not isinstance(items, list) or not items:
        return "- None detected."
    return "\n".join(
        f"- `{item['id']}` **{item['owner']}**: {item['task']} _(status: {item['status']}; review needed)_"
        for item in items
        if isinstance(item, dict)
    )


def previous_action_list(items: object) -> str:
    if not isinstance(items, list) or not items:
        return "- No previous meeting memory supplied."
    return "\n".join(
        f"- `{item['id']}` {item['task']} -> **{item['proposed_status']}**. Evidence: {item['evidence']}"
        for item in items
        if isinstance(item, dict)
    )


def literature_list(items: object) -> str:
    if not isinstance(items, list) or not items:
        return "- None detected."
    return "\n".join(
        "- {question}\n  - Query: `{query}`; importance: {importance}/5; effort: {effort}/5; risk/reward: {score}/5".format(
            question=item["question"],
            query=item["search_query"],
            importance=item["importance"],
            effort=item["estimated_effort"],
            score=item["risk_reward_score"],
        )
        for item in items
        if isinstance(item, dict)
    )


def compact_action_list(items: object, limit: int) -> str:
    if not isinstance(items, list) or not items:
        return "- None detected."
    return "\n".join(f"- {item['owner']}: {item['task']}" for item in items[:limit] if isinstance(item, dict))


def compact_literature_list(items: object, limit: int) -> str:
    if not isinstance(items, list) or not items:
        return "- None detected."
    return "\n".join(f"- `{item['search_query']}` - {item['question']}" for item in items[:limit] if isinstance(item, dict))


def html_list(items: object) -> str:
    if not isinstance(items, list) or not items:
        return "<li>None detected yet.</li>"
    return "\n".join(f"<li>{html.escape(str(item))}</li>" for item in items)


def html_action_list(items: object) -> str:
    if not isinstance(items, list) or not items:
        return "<li>None detected yet.</li>"
    return "\n".join(
        f"<li><strong>{html.escape(str(item['id']))}</strong>: {html.escape(str(item['task']))}</li>"
        for item in items
        if isinstance(item, dict)
    )


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "unknown"


def css() -> str:
    return """
body { margin: 0; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #17201b; background: #f7f5ee; }
main { max-width: 920px; margin: 0 auto; padding: 48px 22px; }
h1 { font-size: clamp(2rem, 4vw, 4rem); line-height: 1; margin: 0 0 18px; }
h2 { margin-top: 34px; border-top: 1px solid #d8d0bf; padding-top: 22px; }
a { color: #245f73; }
li { margin: 8px 0; }
.eyebrow { color: #8f4426; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; }
section { margin-top: 24px; }
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate meeting_heros outputs from a meeting transcript.")
    parser.add_argument("transcript", type=Path, help="Path to a VTT or plain text transcript.")
    parser.add_argument("--meeting-title", default="Lab meeting", help="Human-readable meeting title.")
    parser.add_argument("--meeting-type", default="lab_meeting", help="lab_meeting, sig, one_on_one, or other.")
    parser.add_argument("--previous-memory", type=Path, help="Optional prior meeting_memory.json for action tracking.")
    parser.add_argument("--output", type=Path, default=Path("out"), help="Output directory.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    segments = parse_transcript(args.transcript)
    if not segments:
        raise SystemExit(f"No transcript segments found in {args.transcript}")
    memory = build_memory(args, segments)
    write_outputs(memory, args.output)
    print(f"Wrote meeting_heros outputs to {args.output}")


if __name__ == "__main__":
    main()
