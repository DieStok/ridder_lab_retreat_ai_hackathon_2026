# Automation ideas

A seed list for the Spring 2026 retreat. Pick one, riff on one, or invent your own. None of these are precious — if they spark a better idea, follow the better idea.

Each bullet is a one-line elevator pitch. Pair it with `AGENTS.md` and your coding agent to flesh it out.

## Seed ideas

- **Personal reading digest.** A scheduled bot that watches a Slack channel (or your saved-papers list, or a feed) and emails you a weekly summary of what you missed, grouped by topic.
- **Meeting transcript → summary + enrichment.** Drop a Zoom/MS Teams transcript in; get back action items, decisions, open questions, and links to relevant lab papers/tools mentioned in passing.
- **SIG newsletter to the lab.** Each week, scrape a chosen SIG (preprint feed, journal table of contents, Twitter list) and post a 5-paper digest to a lab Slack channel. Bonus: have it adversarially review one paper per week.
- **Automated `sbatch` profiling and reporting.** Wrap `seff` and friends into a Slack/CLI report that tells you which of your jobs were over- or under-allocated this week, with concrete suggestions to retune `--mem` and `--time`.
- **Reviewing our own papers (locally, IP-safe).** A pipeline that takes a draft (Markdown or PDF), runs an adversarial-review pass with a local LLM (no upload to a remote API), and returns the 3 weakest claims with suggestions. Lab IP never leaves the cluster.
- **Generating interactive demos / paper websites.** From a paper PDF or codebase, generate a small static site with a results browser, a method explainer, and (where applicable) a small interactive widget. Datasets get a similar treatment with a schema-aware browser.
- **Journal Club preparation.** Submit a paper, get back: a 1-paragraph TL;DR, the 3 most important figures with annotations, the canonical critiques from prior literature, and 5 discussion questions ranked by likely fertility.

## Add your own

Open a PR (or just push to your team's branch and the maintainer will merge a batch at the end). Stick to the same one-line-pitch format for additions, and append them under a `## Added during the retreat` heading.

## What makes an idea good for a retreat

- **Bounded.** Achievable demo in 1–3 days.
- **Lab-relevant.** Solves a problem someone in the room actually has, even if only modestly.
- **Has a tight feedback loop.** You can run it, see if it works, and iterate within minutes — not hours.
- **Composes a few existing pieces** rather than inventing a new substrate. Slack + Ollama + a public API is a great shape; a custom transformer architecture is not.

## What makes an idea bad for a retreat

- Requires data the lab doesn't already have access to.
- Requires sustained infrastructure that nobody is willing to maintain after Friday.
- Has a "right answer" hidden behind 3 weeks of fiddly evals.
- Burns through API credits faster than the team can debug.
