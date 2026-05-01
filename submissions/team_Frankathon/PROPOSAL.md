---
team_name: "Frankathon"
team_members:
  - "Franka"
  - "all her friends"
problem:
  number: "new"                 # number from BRAINSTORM_lab_automation_ideas.md (or "new" if invented)
  short_description: "A thorough and exhaustive testing of Dieter\'s work in setting up this ye-old hackathonne."   # one sentence
running_environment: "local"   # one of: local | HPC | cloud_VM | other
                          # HPC implies NO internet access for LLM/agent calls
running_environment_other: ""   # fill only if "other" above
notes_and_caveats: "I am but one measly coder"     # secrets needed, data sensitivity, dependencies on other teams, known blockers
---

# Frankathon — a test of utmost thoroughness


## 1. The problem

We need a hackathon. We need it now. But it remains untested...

## 2. Why it matters & where automation fits

Unfortunately, I need to do it all my by lonesome to ensure it's idiot proof.

## 3. Architecture / workflow

While enjoyable, this is a one-time event occurring locally with little-to-no automation opportunity.

```
Github repo set-up by Dieter The Great
        │
        ▼
Communicated to Franka via Slack
        │
        ▼
Procrastination resulting in coffee chocking
        │
        ▼
Extensive eveluation of repo, including witty comments
        │
        ▼
Feedback to Dieter via Slack
```


## 4. References

I don't need anyone else.

---

## (Bonus) Initial implementation notes

Some notes along the way:
- Perhaps make more explicit whether [additional_information_and_resources](./additional_information_and_resources) contains any information that may be of interest to human readers. I scanned through it and it seems to touch on important considerations for AI automation in our setting. Just context for AI or also context for mai?
- Small snippet on how to download uv: 
```
cd ~/Downloads/
curl -LsSf https://astral.sh/uv/install.sh | sh
# return to your team's directory
cd <path>/ridder_lab_ai_automation/hackathon/submissions/team_<your_team>
```
- Short snippet on how to activate the common venv: `source <path>/ridder_lab_ai_automation/hackathon/.venv/bin/activate`
- Do you recommend working locally? Or do you leave it up to the team?

On my to-do:
- Read the brainstorm document

Demo:
```
python evaluate.py
```


