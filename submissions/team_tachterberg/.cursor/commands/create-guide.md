<!-- GENERATED from .claude/commands/create-guide.md by scripts/sync_agent_commands.py. Edit the source, then re-run the script. -->

You are going to write a complete set of onboarding notebooks for a researcher's project. You will interview them to gather the information you need, then create the notebooks yourself.

The quality of what you produce depends entirely on the quality of information you collect. Push back if answers are vague. Notebooks written from vague answers are useless to new team members and to AI agents.

---

## Phase 1 — Interview

Work through these questions one block at a time. Wait for answers before moving on. Ask follow-up questions if an answer is unclear or underspecified.

### Block A: Project overview
1. What is the project called? (will become the folder name, e.g. `my_project/`)
2. In 2–3 sentences: what biological/scientific question does it address, and what computational approach does it use?
3. What is the current status? (exploration / active development / mature / published)
4. Are there other people working on it with their own copies of the code? If so, name them and their directories — the guide needs to tell new users which copy is canonical.

### Block B: Directory structure
Ask them to give you the key paths. For each one, push for the **full absolute path**, not a variable or relative reference:
- Root analysis directory (where their personal working folder is)
- Main code repository/repositories
- Raw data (exactly where it lives on the filesystem)
- Processed/intermediate data
- Model outputs, results, figures
- Anything that looks important but should be **ignored** (other people's folders, deprecated code, large temp dirs)

> If they give you a relative path or a variable like `$DATA`, ask: "What is the full absolute path starting from /"?

### Block C: Workflows and pipelines
For **each major pipeline step**, collect:
1. What does it do? (one sentence)
2. Exact path to the script or Snakefile
3. Input: what goes in, and where does it come from (full path)?
4. Output: what comes out, and where does it go (full path)?
5. What conda environment runs it? (exact env name)
6. How is it submitted? (sbatch / `--profile Slurm` / directly)
7. What config file does it use, and what are the 2–3 keys a new user must edit?
8. Approximate runtime and resource requirements (CPU/GPU, memory, wall time)

### Block D: First steps for a new user
1. What conda environments need to exist? How are they created?
2. What is the very first thing a new user should do to check their setup?
3. What is the first end-to-end task they should complete to know everything is working?

### Block E: Gotchas and non-obvious things
1. What are the most common mistakes new users make?
2. Is anything named misleadingly or set up in a counterintuitive way?
3. Are there hardcoded paths or usernames in configs that a new user needs to change?
4. What took you a long time to figure out that a new user shouldn't have to rediscover?

---

## Phase 2 — Confirm structure

Based on their answers, propose a set of numbered notebooks. The standard template is:

| # | Notebook | Covers |
|---|----------|--------|
| 01 | `01_introduction.ipynb` | Project background, directory layout, who owns what |
| 02 | `02_data_and_preprocessing.ipynb` | Raw data locations + conversion pipeline(s) |
| 03 | `03_<specific_setup>.ipynb` | E.g. metadata, config, model setup |
| 04 | `04_<main_workflow>.ipynb` | Running the main pipeline / training / analysis |
| 05 | `05_<results>.ipynb` | Reading results, making figures, verifying outputs |

Adjust the structure to fit what you learned. Ask for confirmation before writing.

---

## Phase 3 — Write the notebooks

Create the folder and write all notebooks now. Use the information from the interview.

```bash
mkdir -p <project_name>
```

### Rules for every notebook you write

**Paths:** Always write the full absolute path. Never write a relative path or a shell variable. Wrong: `data/metadata/`. Right: `/hpc/compgen/projects/sturgeon/sturgeoff/analysis/tachterberg/data/metadata/`.

**Code cells:** Every operation described in a markdown cell must have a working code cell underneath it. Do not describe a workflow step without showing the exact command or code to run it.

**What to ignore:** Explicitly name directories and files that look relevant but are not. "Ignore `hvanderent/` and `jbrugger/` — those are other people's analysis forks."

**Environments:** Name the exact conda environment and show the activation command for every workflow that needs one.

**Config keys:** When a config file must be edited, show the relevant section with an example value, not just the key name.

**Counterintuitive things:** If the researcher flagged anything surprising in Block E, add a callout block explaining it.

---

## Phase 4 — Test the guide

Once the notebooks are written, tell the researcher:

> "Your guide is ready. To verify it works, run `/onboard` in this directory and choose your project. If Claude gets confused or has to guess at a path, that's a gap in the documentation — come back to `/create-guide` to fill it in."

Ask if they want to make any adjustments before finishing.
