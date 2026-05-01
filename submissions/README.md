Inside your team dir:
 
- `PROPOSAL.md` — copied from `submissions/TEMPLATE.md`, filled in. The four deliverables go here.
- `README.md` — what you built and how to run it.
- The actual code.
- `.env.example` — if your tool reads tokens.
- Optionally your own `pyproject.toml` if you need deps beyond the shared `hackathon/pyproject.toml`.
- Optionally your own `.venv/` (gitignored).
## Conventions
 
- Don't write outside your own dir during the retreat.
- Don't touch shared hackathon-level files (`README.md`, `pyproject.toml`, `BRAINSTORM_lab_automation_ideas.md`, `AGENTS.md`, `TEMPLATE.md`).
- Don't commit `.env` or model weights.
- Branch as `team/<your_team>` from `main`. Push your branch when ready.
## Submitting
 
```bash
cd ../..                   # back to the hackathon repo root
git add submissions/team_<your_team>
git commit -m "[team_<your_team>] <one-line description>"
git push origin team/<your_team>
```
 
## After the retreat
 
Branches are merged into `main`. Your work stays. If you want to continue the project, lift it out of `submissions/` into its own repo (and submodule of `lab_ai_automation` if it makes sense).
 
<div align="center">
  <img src="../images/cry_a_lot.jpg" alt="Sob" width="600">
</div>
