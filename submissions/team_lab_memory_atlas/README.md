# Lab Memory Atlas

Interactive people/project map for the De Ridder Lab. V2 starts from the question: who is working on what, what changed recently, and who can help?

Meeting transcripts feed the atlas, but draft updates are review-gated before they become lab-visible profile or project context.

## Run

From this directory:

```bash
uv sync
uv run uvicorn app:app --reload --port 8000
```

If `uv` is not available on the machine, use the local virtual environment fallback:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install fastapi "uvicorn[standard]" python-multipart itsdangerous jinja2 pydantic python-dotenv httpx beautifulsoup4 ollama litellm pytest
.venv/bin/python -m uvicorn app:app --reload --port 8000
```

Open <http://127.0.0.1:8000>.

## Admin Dashboard

Create a local `.env` with:

```bash
LAB_ATLAS_ADMIN_PASSWORD=choose-a-real-password
LAB_ATLAS_SESSION_SECRET=generate-a-long-random-string
```

Then restart the app and visit <http://127.0.0.1:8000/admin/login>. Admins can add/edit/archive people, groups, memberships, meetings, actions, literature questions, and review items.

Admins also manage the private action hierarchy:

- enable member login on a person profile and set/reset that member's password or PIN;
- assign one or more supervisors to each PhD or lab member;
- mark global supervisors. Jeroen de Ridder is seeded as the PI/global supervisor automatically.

## Demo Import

Use the existing hackathon transcript:

```text
../../additional_information_and_resources/Teams_transcript_example/Meeting Franka and Paul 20260501.vtt
```

The app accepts VTT or plain text transcripts. It stores local state in `data/demo/state.json`.

## Privacy

Do not commit real transcripts. One-on-one meetings are marked sensitive by default in the review workflow. Meeting-derived updates only become lab-visible after human approval.

Approved action plans are private. A member sees only actions assigned to them, actions assigned to people they supervise, or all actions if they are marked as a global supervisor. Admins can see and repair all actions, including unassigned actions.

## What Works

- Lab roster seeded from the public De Ridder Lab website.
- People/project map as the primary UI.
- Project pages with intro text, slide-style briefs, members, progress, meetings, literature leads, and private-visible action plans.
- Transcript upload and parsing.
- Heuristic extraction with optional Ollama/cloud hooks.
- Review queue for profile updates, action items, and literature questions.
- Action status updates and follow-up prioritization.
- Per-person member login with hashed passwords/PINs.
- Supervisor hierarchy for private action-plan visibility.
- JSON API and static snapshot export.

## What Is Deferred

- Automatic Teams recording.
- Deployment.
- Full paper search through PubMed/arXiv/Semantic Scholar.
- More granular per-record sharing beyond owner/supervisor/global-supervisor visibility.
