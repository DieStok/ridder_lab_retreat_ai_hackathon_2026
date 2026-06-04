# meeting_heros

Meeting memory for the De Ridder lab: turn meeting transcripts into summaries, action points, literature follow-up, collaboration profiles, and Slack-ready lab updates.

## What this prototype does

The hackathon version is transcript-first. It reads a Teams/Zoom VTT file or plain text transcript and generates:

- a meeting digest;
- proposed action points;
- proposed completion status for previous action points;
- literature follow-up ideas ranked by rough risk/reward;
- one HTML collaboration profile per speaker;
- a short Slack-ready lab summary.

Audio transcription is the production path, but not required for the demo. The intended production stack is local transcription first, then a reviewable meeting-memory pipeline.

## Run the demo

From the hackathon repo root:

```bash
python3 submissions/team_meeting_heros/meeting_digest.py \
  additional_information_and_resources/Teams_transcript_example/Meeting\ Franka\ and\ Paul\ 20260501.vtt \
  --meeting-title "Meeting Franka and Paul" \
  --meeting-type "one_on_one" \
  --output submissions/team_meeting_heros/out/demo
```

Then open:

```text
submissions/team_meeting_heros/out/demo/index.html
```

The script uses only the Python standard library.

## Optional action tracking

After one run, pass its `meeting_memory.json` into the next run:

```bash
python3 submissions/team_meeting_heros/meeting_digest.py path/to/new_transcript.vtt \
  --previous-memory submissions/team_meeting_heros/out/demo/meeting_memory.json \
  --output submissions/team_meeting_heros/out/next_meeting
```

The script proposes `likely_done`, `blocked`, or `unknown` statuses with evidence snippets. A human should approve or correct these before sharing lab-wide.

## Privacy note

Generated outputs are designed for lab-internal visibility. One-on-ones, patient-sensitive content, unpublished details, and anything involving people who did not consent should be reviewed before sharing. The real deployment should keep audio and transcripts on lab-controlled storage and use local models by default.

## Next steps

- Replace heuristic extraction with an LLM prompt chain using local Ollama or a reviewed cloud model.
- Add public-paper search through PubMed, arXiv, OpenAlex, or Semantic Scholar.
- Add a review screen for action statuses before publishing.
- Add Slack Bot delivery after creating a test channel and `.env` token setup.
- Add local audio transcription through WhisperX, VibeVoice-ASR-HF, Meetily, or Whishper.
