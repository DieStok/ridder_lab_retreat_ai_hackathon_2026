# `/onboard` — Interactive project onboarding for Claude Code

**Idea #11 · de Ridder Lab Hackathon 2026**

A Claude Code slash command that reads structured project-guide notebooks and interactively walks a new lab member through onboarding onto any Ridder lab project — checking their environment, answering questions, and helping them complete their first real task.

---

## The problem

New lab members spend days figuring out where data lives, which conda environment to use, and how to run the first model. The answers exist only in Slack threads and the heads of whoever set the project up.

## The solution

Two components, both already built:

1. **`project-guides`** — a public GitHub repo of numbered Jupyter notebooks that document each project: what it is, where the data lives, how preprocessing works, how to train the first model, how to make figures.

2. **`/onboard`** — a Claude Code slash command that reads those notebooks and guides a new member through them interactively. It runs read-only verification commands (does the conda env exist? does the data path resolve?), explains things in plain language, and ends by helping them complete a first concrete task.

---

## Installation

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — CLI (`npm install -g @anthropic-ai/claude-code`) or VS Code extension
- Access to the Ridder lab HPC (for the HPC-specific path checks)

### Setup

```bash
# 1. Clone the project-guides repo
git clone https://github.com/TristanAch2001/project-guides.git
cd project-guides

# 2. That's it — the skill is already at .claude/commands/onboard.md
#    Claude Code picks it up automatically from any .claude/commands/ directory
#    in the current repo.
```

### Usage

Open a terminal in the `project-guides` directory and launch Claude Code:

```bash
claude
```

Then type the slash command:

```
/onboard
```

Claude will ask which project you're joining and guide you through the rest.

---

## What it covers (Sturgeon project)

| Step | Notebook | What you learn |
|------|----------|----------------|
| 1 | `01_introduction` | Project background, directory layout, published tools |
| 2 | `02_raw_data_and_preprocessing` | IDAT → CSV → `.dat` memmap pipeline |
| 3 | `03_metadata_setup` | Metadata file format, adding new samples |
| 4 | `04_train_first_model` | Config, Snakemake training on SLURM |
| 5 | `05_umap_visualization` | Computing and plotting UMAPs |

---

## Extending to new projects

Adding onboarding for a new project is a two-step process:

1. **Add notebooks** to `project-guides/<project_name>/` following the same numbered structure.
2. **Update the skill** — add the new project name to the options list in `.claude/commands/onboard.md`.

No code changes, no deployment, no server. The skill picks up new content automatically because it reads the notebooks at runtime.

---

## How the skill works

The skill file (`.claude/commands/onboard.md`) is a plain markdown file with instructions for Claude. When `/onboard` is invoked:

```
User types /onboard
      │
      ▼
Claude reads .claude/commands/onboard.md
      │
      ▼
Claude asks: which project? name?
      │
      ▼
Claude reads notebooks for that project
      │
      ▼
Interactive walkthrough — explains each section,
runs read-only shell checks (conda env list, ls ...)
      │
      ▼
Helps user complete one real first task
      │
      ▼
Summary: key paths, next steps
```

---

## Files in this submission

```
submissions/team_tachterberg/
├── README.md              ← this file
├── PROPOSAL.md            ← design document
└── .claude/
    └── commands/
        └── onboard.md     ← the skill (copy of what's in project-guides)
```

The canonical version of the skill lives in the public `project-guides` repo at:
`https://github.com/TristanAch2001/project-guides`

---

## Testing it yourself

```bash
git clone https://github.com/TristanAch2001/project-guides.git
cd project-guides
claude   # or open in VS Code with Claude Code extension
# type: /onboard
```

If you are not on the Ridder lab HPC, the environment-check steps will show "path not found" — that is expected. The notebooks and the walkthrough still work fully; only the live path verification requires HPC access.
