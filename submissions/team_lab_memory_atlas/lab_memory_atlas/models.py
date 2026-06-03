from __future__ import annotations

from datetime import date, datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class MeetingType(StrEnum):
    LAB_MEETING = "lab_meeting"
    SIG = "sig"
    ONE_ON_ONE = "one_on_one"
    PROJECT = "project"
    OTHER = "other"


class ReviewStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ActionStatus(StrEnum):
    NEW = "new"
    OPEN = "open"
    LIKELY_DONE = "likely_done"
    DONE = "done"
    BLOCKED = "blocked"
    UNCLEAR = "unclear"


class ReviewItemType(StrEnum):
    PROFILE_UPDATE = "profile_update"
    ACTION_ITEM = "action_item"
    ACTION_STATUS = "action_status"
    LITERATURE_QUESTION = "literature_question"


class Person(BaseModel):
    id: str
    name: str
    role: str
    intro: str = ""
    source_url: str = "https://www.deridderlab.nl/"
    topics: list[str] = Field(default_factory=list)
    methods: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    challenges: list[str] = Field(default_factory=list)
    recent_updates: list[str] = Field(default_factory=list)
    action_ids: list[str] = Field(default_factory=list)
    helper_ids: list[str] = Field(default_factory=list)
    supervisor_ids: list[str] = Field(default_factory=list)
    is_global_supervisor: bool = False
    login_enabled: bool = False
    password_hash: str | None = None
    last_seen_meeting_id: str | None = None
    archived: bool = False


class ProjectTopic(BaseModel):
    id: str
    label: str
    kind: str = "topic"
    description: str = ""
    keywords: list[str] = Field(default_factory=list)
    person_ids: list[str] = Field(default_factory=list)
    open_challenges: list[str] = Field(default_factory=list)
    archived: bool = False


class Meeting(BaseModel):
    id: str
    title: str
    meeting_type: MeetingType = MeetingType.LAB_MEETING
    meeting_date: date | None = None
    imported_at: str = Field(default_factory=utc_now)
    source_name: str = ""
    sensitive: bool = False
    summary: str = ""
    decisions: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    speaker_ids: list[str] = Field(default_factory=list)
    topic_ids: list[str] = Field(default_factory=list)
    archived: bool = False


class ActionItem(BaseModel):
    id: str
    owner_id: str | None = None
    title: str
    context: str = ""
    meeting_id: str
    evidence: str = ""
    status: ActionStatus = ActionStatus.NEW
    review_status: ReviewStatus = ReviewStatus.PENDING
    importance: int = 3
    estimated_time: int = 3
    uncertainty: int = 3
    risk_reward: int = 3
    priority_score: int = 0
    archived: bool = False


class LiteratureQuestion(BaseModel):
    id: str
    question: str
    search_prompt: str = ""
    source_person_id: str | None = None
    meeting_id: str
    evidence: str = ""
    review_status: ReviewStatus = ReviewStatus.PENDING
    importance: int = 3
    estimated_time: int = 3
    uncertainty: int = 3
    risk_reward: int = 3
    priority_score: int = 0
    archived: bool = False


class ReviewItem(BaseModel):
    id: str
    item_type: ReviewItemType
    title: str
    proposed_text: str
    payload: dict[str, Any] = Field(default_factory=dict)
    meeting_id: str | None = None
    target_id: str | None = None
    evidence: str = ""
    sensitive: bool = False
    status: ReviewStatus = ReviewStatus.PENDING
    created_at: str = Field(default_factory=utc_now)
    decided_at: str | None = None
    archived: bool = False


class ActivityEvent(BaseModel):
    id: str
    created_at: str = Field(default_factory=utc_now)
    label: str
    detail: str = ""
    person_id: str | None = None
    meeting_id: str | None = None


class AppState(BaseModel):
    generated_at: str = Field(default_factory=utc_now)
    seed_version: int = 0
    people: dict[str, Person] = Field(default_factory=dict)
    projects: dict[str, ProjectTopic] = Field(default_factory=dict)
    meetings: dict[str, Meeting] = Field(default_factory=dict)
    actions: dict[str, ActionItem] = Field(default_factory=dict)
    literature_questions: dict[str, LiteratureQuestion] = Field(default_factory=dict)
    review_items: dict[str, ReviewItem] = Field(default_factory=dict)
    activity: list[ActivityEvent] = Field(default_factory=list)

    def pending_review_count(self) -> int:
        return sum(1 for item in self.review_items.values() if item.status == ReviewStatus.PENDING)

    def approved_actions(self) -> list[ActionItem]:
        return [
            action
            for action in self.actions.values()
            if action.review_status == ReviewStatus.APPROVED
        ]

    def approved_literature_questions(self) -> list[LiteratureQuestion]:
        return [
            question
            for question in self.literature_questions.values()
            if question.review_status == ReviewStatus.APPROVED
        ]
