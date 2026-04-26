# submissions/

One subdirectory per team. Name it `team_<your_name>` (lowercase, underscores). Examples: `team_alice`, `team_journal_club`, `team_sbatch_profiler`.

Inside your team dir:

- `README.md` — what you built and how to run it.
- The actual code.
- `.env.example` — if your tool reads tokens.
- Optionally your own `pyproject.toml` if you need deps beyond what the shared `hackathon/pyproject.toml` provides.
- Optionally your own `.venv/` (gitignored).

## Conventions

- Don't write outside your own dir during the retreat.
- Don't commit `.env` or model weights.
- Branch as `team/<your_name>` from `main`. Push your branch when ready.

## Submitting

```bash
cd ../..                   # back to the hackathon repo root
git add submissions/team_<your_name>
git commit -m "[team_<your_name>] <one-line description>"
git push origin team/<your_name>
```

Open a PR if you want feedback before the merge window.

## After the retreat

Branches are merged into `main`. Your work stays. If you want to continue the project, lift it out of `submissions/` into its own repo (and submodule of `lab_ai_automation` if it makes sense).
