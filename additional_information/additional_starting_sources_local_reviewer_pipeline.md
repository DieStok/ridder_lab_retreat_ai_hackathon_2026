# Additional Starting Sources — Local / Open-Source Multi-Persona LLM Reviewer Pipelines

Landscape map of open-source / local-LLM scientific review systems that
follow the pattern **diverse LLM persona criticisms → distilled final
review or red-team audit** of a paper draft, codebase, or grant proposal.

Anchored on [`isitcredible/reviewer2`](https://github.com/isitcredible/reviewer2)
as the user-supplied exemplar. Proprietary services such as
[refine.ink](https://www.refine.ink/) are explicitly excluded.

---

## Table of contents

- [1. The anchor: how reviewer2 works](#1-the-anchor-how-reviewer2-works)
- [2. Five GitHub repos](#2-five-github-repos)
  - [2.1 AllenAI MARG-Reviewer](#21-allenai-marg-reviewer--the-foundational-one)
  - [2.2 SakanaAI AI-Scientist (v1 + v2)](#22-sakanaai-ai-scientist-v1--v2--ensemble-reviewer-at-scale)
  - [2.3 Ahren09 AgentReview](#23-ahren09-agentreview--controlled-persona-diversity-testbed)
  - [2.4 poldrack/ai-peer-review](#24-poldrackai-peer-review--multi-vendor-llm-meta-review)
  - [2.5 calimero-network/ai-code-reviewer](#25-calimero-networkai-code-reviewer--the-codebase-analogue)
  - [2.6 GitHub honourable mentions](#26-github-honourable-mentions)
- [3. Five academic papers](#3-five-academic-papers)
  - [3.1 MARG](#31-marg-multi-agent-review-generation-for-scientific-papers)
  - [3.2 AgentReview](#32-agentreview-exploring-peer-review-dynamics-with-llm-agents)
  - [3.3 SWIF²T](#33-automated-focused-feedback-generation-for-scientific-writing-assistance-swift)
  - [3.4 The AI Scientist v2](#34-the-ai-scientist-v2)
  - [3.5 DIAGPaper](#35-diagpaper-diagnosing-valid-and-specific-weaknesses-via-multi-agent-reasoning)
  - [3.6 Paper honourable mentions](#36-paper-honourable-mentions)
- [4. Comparison table](#4-comparison-table)
- [5. Practical takeaways](#5-practical-takeaways)

---

## 1. The anchor: how reviewer2 works

[**`isitcredible/reviewer2`**](https://github.com/isitcredible/reviewer2)
(Apache-2.0, v1.0.0 April 2026) runs ~30 LLM stages over a paper PDF as
a directed graph of 46 prompts. Personas are defined as separate prompt
files in `src/reviewer2/prompts/`.

### 1.1 Persona roster

Extracted from prompt filenames in the repo:

- **Red Team:** *Breaker* (interrogates theoretical foundations and
  research design), *Butcher*, *Shredder*, *Collector*.
- **Math audit:** *Math*, *Math-Check*, *Math-Proofread*, *Math-Audit*,
  *Math-Sober*.
- **Code / replication audit:** *Code-Gonzo* (a/b/c), *Code-Compiler*,
  *Code-Checker*, *Code-List*.
- **Blue Team:** *Blue-Team* (writes an honest defence of the paper
  against the Red Team's findings).
- **Reviewer / editor chain:** *Reviewer*, *Data-Editor*, *External*,
  *Reviser*.
- **Polish chain:** *Alchemist*, *Polisher*, *Proofreader*, *Copyedit*.
- **Other:** *Bureaucrat*, *Researcher*, *Thinker*, *Legal*, *Formatter*.

### 1.2 Architecture and output

Each stage is a prompt that reads/writes `.txt` files in a working
directory; they're chained into a directed graph. The final output is a
single plain-text adversarial review (`report.txt`).

### 1.3 Practical caveats

- **Gemini-locked.** The pipeline is hard-coded to the Google Gemini
  API. The `GEMINI_MODEL_OVERRIDE` env var lets you swap which Gemini
  model runs each stage, but there is no Ollama / vLLM / OpenAI-
  compatible support out of the box.
- **Mathpix dependency.** The math-audit add-on (`--math`) requires a
  paid Mathpix account; everything else runs without it.
- **Target.** Published / preprint papers (PDFs). Not designed for
  grants or codebases directly.

The user's pattern — many specialised LLM critics, distilled into a
final audit — is what the rest of this document maps. Priority is given
to projects that are open source and at least redirectable to local
LLMs.

---

## 2. Five GitHub repos

### 2.1 AllenAI MARG-Reviewer — the foundational one

- **Repo:** <https://github.com/allenai/marg-reviewer>
- **Paper:** D'Arcy, Hope, Birnbaum, Downey. *MARG: Multi-Agent Review
  Generation for Scientific Papers*. arXiv:2401.04259 (NAACL 2024).
- **Architecture:** three agent types — a **leader** that coordinates
  communication; **workers** that each consume a chunk of the paper
  (this is what lets the system handle papers longer than the base
  model's context); **expert agents** specialised by comment type
  (experiments / clarity / impact / novelty). The MARG-S variant runs
  several specialised multi-agent groups in parallel, then refines and
  prunes their concatenated comments via a final group.
- **LLM backend:** OpenAI Chat Completions (originally GPT-4) with a
  SQLite cache for reproducibility. Trivially redirectable to any
  OpenAI-compatible local server (Ollama, vLLM, LiteLLM, llama.cpp).
- **Target artefact:** ML/NLP paper PDFs.
- **Headline result from the paper:** generic-comment rate drops 60% →
  29%; good comments per paper rise 1.7 → 3.7 (2.2× over GPT-4
  baselines).
- **Distribution:** Docker image with a small web UI used in the
  original user study.

### 2.2 SakanaAI AI-Scientist (v1 + v2) — ensemble reviewer at scale

- **Repos:**
  - <https://github.com/SakanaAI/AI-Scientist>
  - <https://github.com/SakanaAI/AI-Scientist-v2>
- **Papers:** Lu et al. arXiv:2408.06292 (v1, 2024); Yamada et al.
  arXiv:2504.08066 (v2, 2025). Published in *Nature* in 2026.
- **Architecture (review part):** the system as a whole automates the
  full research lifecycle, but the relevant module is
  `ai_scientist/perform_review.py`. It runs an ensemble of reviewer
  instances (`num_reviews_ensemble=5`) with reflective re-reads
  (`num_reflections=5`), then aggregates the structured outputs
  (Overall, Soundness, Presentation, Contribution, Strengths,
  Weaknesses, Decision) into one review.
- **LLM backend:** pluggable. The README explicitly recommends
  DeepSeek-Coder-V2 for cost reasons and notes that local models can
  substitute via OpenAI-compatible endpoints.
- **Target:** ML papers it generates and reviews. The reviewer module
  is usable standalone on any PDF.
- **Pedigree:** v2 produced the first AI-only paper to clear a real
  double-blind workshop peer review (ICLR 2025 ICBINB).
- **Persona-diversity strategy:** stochastic ensemble + reflection,
  not hand-designed roles — the simplest distillation pattern in this
  list.

### 2.3 Ahren09 AgentReview — controlled persona-diversity testbed

- **Repo:** <https://github.com/Ahren09/AgentReview> (★68; EMNLP 2024
  main, Oral)
- **Paper:** Jin, Zhao, Wang, Chen, Zhu, Xiao, Wang. *AgentReview:
  Exploring Peer Review Dynamics with LLM Agents*. arXiv:2406.12708.
- **Architecture:** five-phase ICLR-style simulation:
  1. Reviewer assessment (independent reviews)
  2. Author rebuttal
  3. Reviewer–AC discussion
  4. Meta-review
  5. Decision
- **Reviewer persona axes:**
  - **Commitment** — responsible vs. lazy
  - **Intention** — benign vs. malicious
  - **Knowledgeability** — knowledgeable vs. unknowledgeable
- **AC styles:** authoritarian, conformist, inclusive.
- **LLM backend:** OpenAI / Azure OpenAI Chat Completions. The
  `BackendType` abstraction makes adding a local OpenAI-compatible
  endpoint a small change.
- **Target:** ML/NLP papers (uses the OpenReview API to pull ICLR
  2020–2023 papers); ships with a Gradio app (`app.py`) for running
  reviews on your own PDFs.
- **Why it stands out:** the cleanest implementation of *deliberate*
  persona diversity. The paper itself analyses how the persona mix
  shifts the distilled outcome (anchoring bias, social-influence
  drift, altruism fatigue — e.g. one "lazy" reviewer drops engagement
  18.7%).

### 2.4 poldrack/ai-peer-review — multi-vendor LLM meta-review

- **Repo:** <https://github.com/poldrack/ai-peer-review> (Russell
  Poldrack, Stanford neuroscience)
- **Architecture:** the simplest, most direct realisation of the
  user's pattern. A paper PDF is sent to several LLMs in parallel,
  each given a domain-expert persona prompt ("You are a neuroscientist
  and expert in brain imaging…"), spanning OpenAI, Anthropic, Google,
  and Together AI (DeepSeek R1, Llama-4-Maverick). The individual
  reviews are then synthesised into a single meta-review by another
  LLM call that highlights shared and divergent concerns.
- **LLM backend:** deliberately multi-vendor. Persona diversity comes
  from genuinely different model *families*, which mitigates
  single-model bias more than same-model role-play does. Trivially
  extendable to Ollama / local LLMs by editing the provider table.
- **Target:** scientific papers in any field. Developed for
  neuroscience but general.
- **Why it fits exceptionally well:** it's the closest in spirit to
  "diverse personas → distilled review" because the diversity is
  across model families rather than across prompts of one model.

### 2.5 calimero-network/ai-code-reviewer — the codebase analogue

- **Repo:** <https://github.com/calimero-network/ai-code-reviewer>
- **Architecture:** 2–5+ specialised LLM agents run in parallel, each
  focused on one perspective:
  - *Security*
  - *Performance*
  - *Code quality*
  (the role table is extensible). Findings are weighted by inter-agent
  agreement (consensus-based scoring), then merged into a unified
  review with confidence scores. Integrates with GitHub via PR
  webhooks for inline comments and thread resolution.
- **LLM backend:** Anthropic Messages API only (Claude Opus 4.6,
  Sonnet 4.6) at the time of writing. The code is OSS but inference is
  Anthropic-locked; porting to a local OpenAI-compatible backend is a
  thin SDK swap.
- **Target:** pull requests / repositories. Covers the codebase audit
  leg of the user's question, complementing the paper-focused systems
  above.
- **Why it fits:** explicit specialised-persona + consensus
  distillation — the same conceptual pattern as reviewer2, applied to
  code.

### 2.6 GitHub honourable mentions

- **`maxidl/openreviewer`** — Llama-OpenReviewer-8B fine-tuned on
  79k expert reviews, with HuggingFace Spaces demo (NAACL 2025 demo
  paper). Runs locally on a single consumer GPU. *Not* multi-persona —
  a single specialised reviewer model — so it's a different design
  point, but very relevant for the local-LLM angle.
- **Multi-agent debate + Z3 / Knuckledragger** repo seen on the GitHub
  `paper-review` topic page — formal verification of paper claims via
  multi-agent debate with proof certificates. Niche but interesting;
  couldn't pin down the exact repo name in time.
- **AgentRxiv** — preprint-server-style sharing of LLM-generated
  research, with reviewer agents as part of the loop.
- **CycleResearcher / SciAgents / ResearchAgent** — full
  research-pipeline systems with internal review steps; broader than
  just review.

---

## 3. Five academic papers

### 3.1 MARG: Multi-Agent Review Generation for Scientific Papers

- **Authors and venue:** D'Arcy, Hope, Birnbaum, Downey (Allen Institute
  / Northwestern). arXiv:2401.04259, NAACL 2024.
- **Architecture:** agents = chat-LLM instances. Three roles: **leader**
  (coordinates), **workers** (each gets a chunk of the paper), **expert
  agents** (specialise in one comment type — experiments, clarity,
  impact). The MARG-S variant runs several specialised multi-agent
  groups in parallel, then refines/prunes their concatenated comments
  via a final group.
- **Headline result:** cuts generic-comment rate from 60% → 29%; raises
  good comments per paper from 1.7 → 3.7 (2.2× over GPT-4 baselines).
- **Why it matters:** the closest single-paper analogue to the user's
  pattern. Defines the template the rest of the field is iterating on.
- **Code:** [allenai/marg-reviewer](https://github.com/allenai/marg-reviewer).

### 3.2 AgentReview: Exploring Peer Review Dynamics with LLM Agents

- **Authors and venue:** Jin et al. arXiv:2406.12708, EMNLP 2024 main
  track (Oral).
- **Architecture:** five-phase simulation of an ICLR-style conference.
  Roles = reviewers, authors, ACs. Persona diversity from three
  orthogonal attribute axes per reviewer (Commitment × Intention ×
  Knowledgeability) and three AC styles. Each persona is an
  independently-prompted LLM agent.
- **Distillation:** per-reviewer reviews → reviewer–AC discussion →
  meta-review → accept/reject decision.
- **Why it matters:** the strongest published evidence that *which*
  personas you instantiate changes the distilled outcome. Includes
  analyses of anchoring bias, social-influence drift, altruism
  fatigue.
- **Code:** [Ahren09/AgentReview](https://github.com/Ahren09/AgentReview).

### 3.3 Automated Focused Feedback Generation for Scientific Writing Assistance (SWIF²T)

- **Authors and venue:** Chamoun, Schlichtkrull, Vlachos (Cambridge).
  arXiv:2405.20477, ACL Findings 2024.
- **Architecture:** four LLM components:
  - **Planner** — produces a focused feedback plan, re-ranked for
    coherence/specificity.
  - **Investigator** — literature-augmented evidence-gathering.
  - **Reviewer** — writes the comment given plan + evidence.
  - **Controller** — manages plan progression and coordinates the
    others.
- **Targets:** weakness-spotting in specific paragraphs across five
  aspects — Replicability, Originality, Soundness, Meaningful
  Comparison, Substance.
- **Headline result:** beat GPT-4 and CoVe on specificity, reading
  comprehension, and helpfulness in human evaluation. In some cases
  reviewers preferred the SWIF²T comments to the original human ones.
- **Why it matters:** strong match for the user's pattern because (a) it
  decomposes review into specialised LLM calls and (b) it uses an
  explicit re-ranking/distillation step over candidate plans, not just
  majority voting.
- **Code:** [ericchamoun/FocusedFeedbackGeneration](https://github.com/ericchamoun/FocusedFeedbackGeneration).

### 3.4 The AI Scientist v2

- **Full title:** *The AI Scientist-v2: Workshop-Level Automated
  Scientific Discovery via Agentic Tree Search.*
- **Authors and venue:** Yamada et al. arXiv:2504.08066 (v2, 2025).
  Preceded by Lu et al. arXiv:2408.06292 (v1, 2024). The system as a
  whole was published in *Nature* in 2026.
- **Architecture (review part):** built-in Automated Reviewer runs an
  ensemble of reviewer LLM instances (`num_reviews_ensemble=5`) with
  reflective passes per reviewer (`num_reflections=5`), then aggregates
  into a structured review covering Overall, Soundness, Presentation,
  Contribution, Strengths, Weaknesses, Decision.
- **Persona-diversity strategy:** stochastic ensemble + reflection,
  rather than hand-designed roles — the simplest distillation pattern
  in this list.
- **Why it matters:** the v2 produced the first fully AI-generated paper
  to pass a real double-blind workshop peer review (ICLR 2025
  ICBINB).
- **Code:** [SakanaAI/AI-Scientist](https://github.com/SakanaAI/AI-Scientist),
  [SakanaAI/AI-Scientist-v2](https://github.com/SakanaAI/AI-Scientist-v2).

### 3.5 DIAGPaper: Diagnosing Valid and Specific Weaknesses via Multi-Agent Reasoning

- **Authors and venue:** Zou, Ansari, Zhang, Lee, Yin (Penn State,
  Sheffield). arXiv:2601.07611 (Jan 2026).
- **Architecture:** three tightly coupled modules:
  - **Customizer** — infers paper-specific evaluation criteria and
    instantiates *multiple reviewer agents with criterion-specific
    expertise*. Personas are derived from the paper itself rather than
    hard-coded.
  - **Reviewer agents** — produce candidate weaknesses.
  - **Rebuttal-style validation module** — simulates author rebuttals
    to validate or discard each weakness, addressing the well-known
    false-weakness problem in MARG-style systems.
- **Output:** a *ranked* list of consequential issues, not an unranked
  dump.
- **Why it matters:** directly addresses three failure modes the user
  cares about — surface-level role-play, unvalidated weaknesses, and
  unranked output. The most current and most refined of the five.

### 3.6 Paper honourable mentions

- **Generative Reviewer Agents (GAR)** — Tan et al., EMNLP 2025
  Industry Track — granular persona memory + graph-based paper
  representation + memory-augmented multi-round evaluation.
- **MAMORX** — extends MARG with multi-modal (figure) and external-
  knowledge agents.
- **TreeReview** — Chen et al. arXiv:2506.07642 (2025) — replaces
  fixed personas with a dynamic tree-of-questions search. Same
  problem, different shape: fewer agents, more depth.
- **ReviewAgents** — Wang et al. arXiv:2503.08506 (2025) — multi-role,
  multi-LLM, fine-tuned on a 142k-comment Review-CoT dataset.
- **ReviewerGPT** — Liu & Shah, arXiv:2306.00622 (2023) — earliest
  exploratory study on LLMs as paper reviewers; useful as a baseline.
  Finds that task-specific prompting beats "write me a review".
- **MultiCritique** — Lan et al. arXiv:2410.15287 (2024) — uses
  multi-agent feedback to *train* better critics; complementary to
  inference-time pipelines.
- **Peer Review as a Multi-Turn and Long-Context Dialogue with
  Role-Based Interactions** — Tan et al. (2024) — earlier role-based
  dialogue framing that AgentReview builds on.
- **Liang et al., NEJM AI 2024** — *Can LLMs Provide Useful Feedback
  on Research Papers? A Large-Scale Empirical Analysis* — large
  single-LLM baseline that motivates almost all the multi-agent line
  of work.
- **An LLM-based Multi-Agent Collaborative Approach for Abstract
  Screening towards Automated Systematic Reviews** — medRxiv 2025 —
  same multi-LLM pattern (majority voting / multi-agent debate /
  adjudication) applied to systematic-review screening rather than
  full paper review. A useful empirical comparison of distillation
  strategies.

---

## 4. Comparison table

| Project | Type | Personas | Distillation | LLM backend | Target |
|---|---|---|---|---|---|
| reviewer2 *(anchor)* | Code | ~30 (Red Team, Blue Team, Math, Code, Polish) | Hand-engineered DAG of 46 prompts | Gemini API only | Paper PDF |
| MARG | Code + paper | Leader / Workers / Experts | Refinement group | OpenAI (any compatible) | Paper PDF |
| AI Scientist v2 | Code + paper | Ensemble of N reviewers + reflections | Aggregate over ensemble | OpenAI / Anthropic / DeepSeek / any | Paper (also generates) |
| AgentReview | Code + paper | Reviewer × 3 attribute axes + AC × 3 styles | Reviewer–AC discussion → meta-review | OpenAI / Azure | Paper PDF |
| poldrack/ai-peer-review | Code | One per LLM vendor with domain prompt | Meta-review LLM call | OpenAI / Anthropic / Google / Together | Paper PDF |
| calimero ai-code-reviewer | Code | Security / Performance / Quality | Consensus-weighted merge | Anthropic only | Code / PR |
| SWIF²T | Paper + code | Planner / Investigator / Reviewer / Controller | Plan re-ranking | OpenAI | Paper paragraphs |
| DIAGPaper | Paper | Derived from paper at runtime | Rebuttal validation + ranking | OpenAI | Paper PDF |
| OpenReviewer | Code + paper | Single fine-tuned model | n/a (single model) | Local Llama-8B | Paper PDF |

---

## 5. Practical takeaways

### 5.1 Backend portability is mostly free

Every system in the table that uses the OpenAI Chat Completions schema
runs against Ollama, vLLM, llama.cpp, or LiteLLM with a `base_url`
change and an env var. The two that *don't* fit cleanly into a
local-LLM workflow are:

- **reviewer2** — Gemini-locked.
- **calimero ai-code-reviewer** — Anthropic-locked.

**poldrack/ai-peer-review** is the only system that builds backend
diversity in by design, treating different vendors as different
personas.

### 5.2 Persona diversity vs. distillation strategy is the real design space

If you're building your own pipeline, four named ends of the design
space are worth picking from:

1. **Hand-engineered roles + simple distillation** — reviewer2, MARG.
   Maximum control, maximum prompt-engineering effort.
2. **Stochastic ensemble + reflection** — AI Scientist. Minimal role
   design, relies on temperature and self-critique for diversity.
3. **Parameterised persona attributes** — AgentReview. Lets you ablate
   which axes of reviewer behaviour matter.
4. **Runtime-derived personas with validation** — DIAGPaper. The most
   recent design point; personas come from the paper, weaknesses are
   rebuttal-validated, output is ranked.

A fifth option, **vendor-as-persona** (poldrack/ai-peer-review), sits
orthogonally: instead of varying prompts, vary model families.
