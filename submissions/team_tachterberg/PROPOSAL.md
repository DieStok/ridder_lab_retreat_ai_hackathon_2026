---
team_name: "tachterberg"
team_members:
  - "Tristan Achterberg"
problem:
  number: 11
  short_description: "A Claude Code slash command that reads project-guide notebooks and interactively onboards new lab members onto any Ridder lab project."
running_environment: "HPC"
running_environment_other: ""
notes_and_caveats: "Requires Claude Code (CLI or VS Code extension). Notebooks reference HPC file paths — remote members would need to adapt paths or use SSH port-forwarding. No LLM API key needed beyond the standard Claude Code subscription."
---

# Team Tachterberg — `/onboard`: an interactive project onboarding skill for Claude Code

## 1. The problem

New lab members joining an ongoing project — whether a PhD student, rotation student, or collaborator — face a steep learning curve. Where is the data? Which conda environment do I use? How do I run the first model? The answers are scattered across lab wikis, Slack messages, and the heads of whoever set the project up. Onboarding takes days instead of hours, and the person who set up the project is constantly interrupted to explain the same things.

## 2. Why it matters & where automation fits

Each new project member costs the PI and senior lab members significant interruption time. Worse, undocumented tribal knowledge means that if the original developer leaves, the knowledge walks out the door with them.

The fix has two parts:
1. **Structured notebooks** (`project-guides`) that document what the project is, where the data lives, how preprocessing works, how to train the first model, and how to make figures.
2. **A Claude Code slash command** (`/onboard`) that reads those notebooks and guides a new member through them *interactively* — checking their environment, running verification commands, and answering follow-up questions on the spot.

The LLM's role is specifically suited to this: reading structured documentation and re-explaining it conversationally, adapting to the user's level of understanding, and running read-only diagnostic commands to confirm things actually work.

## 3. Architecture / workflow

```
New team member opens the project-guides repo in VS Code / Claude Code terminal
        │
        ▼
types /onboard
        │
        ▼
Claude reads .claude/commands/onboard.md (the skill)
        │
        ▼
Claude asks: which project? (sturgeon / foundation / ...)
        │
        ▼
Claude reads the project's numbered notebooks (01_intro, 02_data, 03_metadata, ...)
        │
        ▼
Interactive walkthrough — explains each section, runs verification commands
(conda env list, ls /hpc/..., loads a sample .dat or metadata file)
        │
        ▼
New member completes a first concrete task (load a file, read metadata, etc.)
        │
        ▼
Summary: key paths, next steps, open questions
```

The skill itself is a single markdown file. No server, no API calls beyond Claude Code, no deployment infrastructure needed. A new project is onboarded simply by adding notebooks to `project-guides/` and updating the skill's project list.

## 4. References

- Claude Code slash commands / skills: https://docs.anthropic.com/en/docs/claude-code/slash-commands
- `project-guides` repo (public): https://github.com/TristanAch2001/project-guides

## (Bonus) Initial implementation notes

The `project-guides` repo already contains:
- `sturgeon/` — five notebooks: introduction, preprocessing (IDAT→CSV→.dat), metadata setup, model training, UMAP visualisation
- `.claude/commands/onboard.md` — the skill file (ready to use)

To demo: clone `project-guides`, open in VS Code with the Claude Code extension, type `/onboard`.
