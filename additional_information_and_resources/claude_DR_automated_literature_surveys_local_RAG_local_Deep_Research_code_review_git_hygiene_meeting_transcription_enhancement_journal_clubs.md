# AI/LLM-Augmented Computational Lab Automation Landscape — Inputs & Daily Work (Parts 1–5), April 2026

*Prepared for a 5–25-person academic computational research lab (bioinformatics / ML / computational science) with HPC access, mixed laptops, and unpublished or sensitive data.* The advice below is opinionated. It privileges open source, self-hostable, and local-LLM-friendly options over polished SaaS. Where a tool's claims and its repo state diverge, that gap is called out explicitly. Where I could not verify a number or post after at least three searches, I say so.

---

## Part 1 — Automated Literature Surveys, Lab-Local RAG, and Local Deep-Research Workflows

### 1.1 Cloud personalized literature feeds

#### Scholar Inbox
| | |
|---|---|
| (a) What it does | Daily personalized arXiv/bioRxiv/medRxiv/ChemRxiv digest based on a logistic-regression recommender trained on your explicit ratings, plus a 2-D "map of science" visualization. |
| (b) Hosting model | SaaS only ([scholar-inbox.com](https://scholar-inbox.com)). |
| (c) Local-LLM support | None — it is a recommender, not a RAG system. |
| (d) License + maintenance | Free for academics; closed core; ACL 2025 demo paper ([arXiv:2504.08385](https://arxiv.org/abs/2504.08385)); actively developed by the Geiger lab at Tübingen. |
| (e) Integration overhead | 5-min sign-up; rate ~50 papers to bootstrap. |
| (f) Privacy | You upload only positive/negative ratings. The recommender is content-based on title/abstract embeddings — paper *content* is not exfiltrated, but your interest profile is held by the service. |
| (g) Failure modes | Coverage outside CS/bio is thin; cold-start still needs ~50 ratings before the digest stabilizes (see [Flicke et al., ACL 2025](https://aclanthology.org/2025.acl-demo.30/)). |
| (h) Lab fit verdict | **Adopt now** as the lab-wide replacement for Google Scholar Alerts. Free, zero IT footprint. |

#### Elicit, Consensus, Undermind, SciSpace, Perplexity (commercial baselines)
These are SaaS products that do question-driven search over scholarly indexes. **Undermind** is the strongest performer in independent librarian-blind tests, with [Aaron Tay's review](https://aarontay.substack.com/p/ai2-paper-finder-and-futurehouse) calling it his current benchmark; FutureHouse's free **Crow/Falcon/Owl** suite (built on PaperQA2) and **Ai2 Paper Finder** are now competitive and far more transparent. **Consensus** and **Elicit** are useful for finding claim-level evidence but have been criticized for over-confident summaries. **Perplexity Pro Spaces** is a generic web-grounded chatbot dressed up as research assistant — fine for triage, weak for citation discipline. None has been peer-reviewed against the others in a published systematic head-to-head as of April 2026 [unable to verify any independent peer-reviewed benchmark]. **All five send query and (in some cases) PDF content to vendor servers** — disqualifying for unpublished or patient-derived corpora.

| Tool | Best at | Free-academic tier? | Privacy verdict |
|---|---|---|---|
| Scholar Inbox | personalized daily feed | yes | preferences live on server |
| Undermind | precision search on a topic | trial only | queries leave premises |
| FutureHouse Crow/Falcon/Owl ([futurehouse.org](https://www.futurehouse.org)) | agentic Q&A over PubMed + OA | yes | queries leave premises |
| Ai2 Paper Finder | transparent step-by-step search | yes | queries leave premises |
| Elicit / Consensus | claim-level evidence tables | partial | queries leave premises |
| Perplexity Pro Spaces | generic web Q&A | paid | queries leave premises |

### 1.2 Self-hostable deep-research clones

#### PaperQA2 (Future-House/paper-qa)
| | |
|---|---|
| (a) | Agentic RAG over a folder of PDFs, with retraction checks, OpenAlex metadata, contextual re-ranking and contradiction detection. |
| (b) | Library; runs anywhere Python runs. |
| (c) | Works against any LiteLLM-compatible endpoint, so Ollama, vLLM, llama.cpp, OpenAI-compatible servers all work out of the box ([github.com/Future-House/paper-qa](https://github.com/Future-House/paper-qa)). |
| (d) | Apache-2.0; ~7,000 stars, ~700 forks; very actively maintained as of April 2026 (recent breaking-change v5 rename). |
| (e) | `pip install paper-qa` then `pqa ask` — a 5-minute install. Lab-scale ingestion of 5,000+ PDFs is a weekend project. |
| (f) | Strong: PDFs and embeddings can stay entirely on lab hardware. |
| (g) | LitQA2 and RAG-QA-Arena science scores (12.4 points above the closest competitor, [FutureHouse blog](https://www.futurehouse.org/research-announcements/paperqa2-achieves-sota-performance-on-rag-qa-arena-science-benchmark)) are vendor-reported. The original [arXiv:2409.13740](https://arxiv.org/abs/2409.13740) "superhuman" claim is over a small biology-PhD comparison group (n≈9) — treat as suggestive, not settled. |
| (h) | **Best-in-class for "RAG over my PDFs". Adopt now.** |

#### LangChain `open_deep_research`
- **What:** Reference implementation of a multi-step research agent that summarizes search results into a long-form report, evaluated on Deep Research Bench (RACE 0.4344, rank ~6 as of Aug 2025) ([github.com/langchain-ai/open_deep_research](https://github.com/langchain-ai/open_deep_research)).
- **Local-LLM:** Yes via Ollama or any OpenAI-compatible endpoint, but the README's own Deep Research Bench numbers were collected with `gpt-4.1` / `gpt-5`. Vendor-claimed parity with closed agents is **not** independently reproduced for local 70B-class models.
- **Verdict:** Worth piloting if the lab already runs LangGraph; otherwise a heavyweight dependency for a moderate gain.

#### Local Deep Research (LearningCircuit/local-deep-research)
- **What:** Self-hostable agent that searches arXiv, PubMed, SearXNG, the open web and your private docs, with an optional LangGraph-agent strategy. README claims ~95 % on SimpleQA with `gpt-4.1-mini` ([github.com/LearningCircuit/local-deep-research](https://github.com/LearningCircuit/local-deep-research)) — a vendor-self-report, not peer-reviewed.
- **Local-LLM:** First-class via Ollama; encrypted local library is part of the design.
- **Verdict:** **The first thing to pilot if your data must never leave the lab.** Pair with a lab SearXNG instance.

#### GPT Researcher (assafelovic/gpt-researcher)
- A long-running open-source deep-research agent with broad community use; works against Ollama and OpenAI-compatible endpoints. There is no recent independent benchmark; it is best understood as an early reference design and is increasingly being wrapped inside other systems (e.g. as an Open WebUI pipe — see [open-webui discussion #9321](https://github.com/open-webui/open-webui/discussions/9321)).

#### STORM / Co-STORM (stanford-oval/storm)
- LLM-driven Wikipedia-style article generator. ~25 k stars; backed by a published EMNLP paper. Works with local models via DSPy (see [DigitalOcean tutorial](https://www.digitalocean.com/community/tutorials/stanford-oval-storm-mistral-demo)). Excellent for *outline-shaped* surveys; weaker than PaperQA2 at PDF-grounded factual QA. **Adopt** as a "first draft of a related-work section" tool, not as a literature-search system.

#### Open WebUI research pipelines / Khoj
- **Open WebUI** (~70 k+ stars, MIT) ships a pipeline architecture; community pipes wrap STORM, GPT Researcher and OpenAI's o3-deep-research. The architecture is ergonomic but, by the maintainers' own admission ([discussion #9321](https://github.com/open-webui/open-webui/discussions/9321)), proper deep-research requires re-architecting the chat-completion flow. Treat current pipes as alpha.
- **Khoj** ([github.com/khoj-ai/khoj](https://github.com/khoj-ai/khoj)) is a self-hostable second-brain agent over PDFs, Markdown, Notion and Org files, with strong Ollama/llama.cpp/vLLM support. It is the most polished "personal NotebookLM alternative" and the easiest entry point for a non-engineer in the lab.

#### Continue.dev (as a "PaperQA-lite")
- Continue is primarily a coding assistant (Part 2) but its custom-doc index lets a lab engineer point it at a folder of papers and chat across them locally — a sensible bridge for engineers already living in VS Code.

### 1.3 Lab-local knowledge-base patterns — the recipe

The 2026 default recipe for a lab-local scientific RAG looks like this:

1. **Ingest.** Choose by document type:
   - **Marker** ([github.com/VikParuchuri/marker](https://github.com/VikParuchuri/marker)) — fastest "PDF-to-markdown", strong on text-heavy preprints. CC-BY-NC-SA model weights — flag for industrial spinoffs.
   - **Docling** (IBM, [github.com/docling-project/docling](https://github.com/docling-project/docling), Apache-2.0) — best layout/structure fidelity for downstream NLP; integrates with LangChain/LlamaIndex; AAAI 2025 paper [arXiv:2501.17887](https://arxiv.org/pdf/2501.17887) reports 0.49 sec/page on an L4. **Default for lab pipelines.**
   - **MinerU** (OpenDataLab, [arXiv:2409.18839](https://arxiv.org/abs/2409.18839), AGPL-3.0) — wins on layout-detection benchmarks (97.5 mAP) and complex tables/equations; ideal for math-heavy or non-English papers; AGPL is the catch.
   - **Grobid** — still the right choice for citation/metadata extraction at scale.
   - **Nougat** — math-aware, but less actively maintained than Marker/Docling.
   - **ColPali** ([arXiv:2407.01449](https://arxiv.org/abs/2407.01449)) — direct visual embedding of PDF pages; outperforms OCR pipelines on figure-heavy and tabular content (ViDoRe benchmark) but storage- and compute-hungry, and an independent 2025 study ([arXiv:2505.05666](https://arxiv.org/pdf/2505.05666)) shows OCR-based RAG generalizes better to *unseen* document types. Use ColPali when figures or tables actually drive your retrieval.
2. **Embed.** Use **Qwen3-Embedding-0.6B** (Apache-2.0) as the modern default — it ranked #1 on MTEB multilingual at release (score 70.58, [Qwen3-Embedding repo](https://github.com/QwenLM/Qwen3-Embedding)). **BGE-M3** (BAAI, MIT) remains a strong, smaller hybrid (dense + sparse + multi-vector) baseline. For science-only corpora, **SciNCL** still beats general-purpose embeddings on niche tasks but is dated; no peer-reviewed evidence shows that a "scientific" embedding outperforms Qwen3-Embedding-8B on broad scientific retrieval as of April 2026.
3. **Re-rank.** **Qwen3-Reranker-0.6B / 4B** (Apache-2.0) and **BGE-Reranker-v2-m3** are the open defaults; both run via TEI/Infinity.
4. **Store.** **Qdrant** for production-grade hybrid search; **Chroma** for laptops; **LanceDB** for embedded; **Postgres + pgvector** when the lab already runs Postgres. Weaviate is a fine alternative; the differences are operational.
5. **Generate.** Any LiteLLM-compatible endpoint — Ollama, vLLM, SGLang — running a 30B-class instruct model is now sufficient for most QA. The April-2026 [whatllm.org open-source ranking](https://whatllm.org/best-open-source-llm) puts Kimi K2.6, GLM-5/4.7 and DeepSeek V4-Flash at the top of the open-weights leaderboard.
6. **Zotero plumbing.** Aria / ARIA-Zotero, the "Zotero AI / Beaver" plugins and the [Khoj Obsidian/Zotero connectors](https://github.com/khoj-ai/khoj) all let researchers stay inside their reference manager. Zotero's own native AI features were still alpha as of early 2026 — verify before standardising.

### 1.4 Embedding models for science

| Model | License | Open | Notes |
|---|---|---|---|
| **Qwen3-Embedding-0.6B / 4B / 8B** | Apache-2.0 | yes | MTEB multilingual #1 at release; instruction-aware; matryoshka 32–1024 dims ([arXiv:2506.05176](https://arxiv.org/pdf/2506.05176)). |
| **BGE-M3** | MIT | yes | Multi-functionality (dense+sparse+multi-vec), 100+ languages, 8192-token context. Default for hybrid retrieval. |
| **NV-Embed-v2** | NV community | yes | Strong on MTEB; license restricts commercial use. |
| **mxbai-embed-large**, **Jina v3/v5** | mixed | yes | Solid generalists; Jina has multimodal v5. |
| **EmbeddingGemma-300M** | Gemma | yes | Tiny, multilingual, suitable for laptop-side caching. |
| **SciNCL** | MIT | yes | Older, science-only. Useful only for niche scholarly tasks. |
| **ColPali / ColQwen2** | Gemma research | yes | Visual document embeddings; the right choice when figures/tables drive retrieval. |

All of the above run cleanly via **Hugging Face TEI**, **Infinity**, or **Ollama** (for the GGUF-quantized variants).

### 1.5 First-hand adoption posts

- **Andrew White (FutureHouse co-founder)** announced PaperQA2 on Bluesky and LinkedIn — "the first agent to beat PhD and Postdoc-level biology researchers on multiple literature research tasks" ([LinkedIn announcement](https://www.linkedin.com/posts/andrewdwhite_today-futurehouse-has-released-paperqa2-activity-7239691606931488774-N9Lj)). His Bluesky handle is `@andrew.diffuse.one` (linked from [github.com/whitead](https://github.com/whitead)).
- **Aaron Tay (academic librarian, Singapore Management University)** runs the [aarontay.substack.com](https://aarontay.substack.com/p/ai2-paper-finder-and-futurehouse) blog and has put PaperQA2-Crow, Ai2 Paper Finder and Undermind through head-to-head librarian-style tests: "*two academic deep search/research tools that caught my attention: Ai2 Paper Finder and Futurehouse's PaperQA2-based search. These two tools are currently free, and perform at roughly the same level as my current favourite Deep Search Academic tool — Undermind.ai.*"
- **Rob Lanfear (ANU, evolutionary biology)** publishes the [phypapers literature-bot recipe](https://github.com/roblanf/phypapers) for posting curated arXiv/bioRxiv feeds to Bluesky — a low-tech but widely copied pattern: "*Casey Bergman started it all with a Drosophila literature bot called flypapers back when Twitter existed.*"
- **Patrick Mineault (NeuroAI, Amaranth Foundation)** maintains the [neuroai.science Substack](https://www.neuroai.science/) and on Bluesky (linked from [his About page](https://xcorr.net/about/)) has written "ML tools for scientists" recommending NotebookLM for cross-referencing 50-PDF corpora and Claude as his daily driver, while flagging the data-training concern.

### 1.6 Editorial — what to actually pilot in Q3

If you have one analyst-month of budget, do exactly two things. **First**, deploy **PaperQA2** on a single workstation (or one A100 node) pointed at the lab Zotero library, ingested via **Docling**, embedded with **Qwen3-Embedding-0.6B**, served from **Ollama** with **GLM-4.7-Air** or **Qwen3-30B-A3B-Instruct**. Budget: ~3 person-days for the engineer, ~$0 for software, ~24 GB VRAM. This becomes the lab's "ask the literature" interface. **Second**, get every PI and postdoc on **Scholar Inbox** so their personal triage stops happening over Google Scholar email alerts. Budget: 30 minutes per person, $0. If you can stretch a bit further, stand up **Local Deep Research** on the same machine for long-form survey writing — it is the deep-research clone that most respects the privacy bar an academic lab actually needs.

What I would *not* do this quarter: build a STORM- or LangChain-`open_deep_research`-based survey agent from scratch. The benchmark numbers are still vendor-self-reports, the implementations move weekly, and PaperQA2 already covers the highest-value use case (grounded Q&A over your PDFs).

### Part 1 comparison table

| Tool | Hosting | Local-LLM | License | Lab fit |
|---|---|---|---|---|
| Scholar Inbox | SaaS | n/a | free academic | adopt now |
| PaperQA2 | self-host | yes (LiteLLM) | Apache-2.0 | adopt now |
| Local Deep Research | self-host | yes (Ollama) | MIT-ish | pilot Q3 |
| Khoj | self-host | yes | AGPL | pilot Q3 |
| Open WebUI + research pipe | self-host | yes | BSD-3-style | watch |
| LangChain `open_deep_research` | self-host | yes | MIT | watch |
| GPT Researcher | self-host | yes | Apache-2.0 | watch |
| STORM | self-host | yes (DSPy) | MIT | adopt for surveys |
| Undermind / Ai2 Paper Finder | SaaS | n/a | free/paid | use as cross-check |
| Marker / Docling / MinerU | self-host | n/a | MIT/Apache/AGPL | Docling default |

---

## Part 2 — Automated Code Review and Code Improvement

### 2.1 Interactive coding agents

#### Claude Code (Anthropic)
| | |
|---|---|
| (a) | Terminal-and-IDE coding agent with subagents, Skills, hooks, slash commands, parallel Task spawning, GitHub Action and Sandbox; the canonical "long-running agent" for scientific computing per [Anthropic's own write-up](https://www.anthropic.com/research/long-running-Claude). |
| (b) | SaaS API (Anthropic) + a local TUI/IDE binary; **not self-hostable.** Some users route via `claude-code-router` to llama-server. |
| (c) | Officially Anthropic models only; community routers (claude-code-router, llama.cpp's instructions in [discussion #14758](https://github.com/ggml-org/llama.cpp/discussions/14758)) plug in local models with caveats. |
| (d) | Proprietary; CLAUDE.md / AGENTS.md / SKILL.md conventions are open and widely copied; ecosystem includes [VoltAgent's 100+ subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) and [matsengrp/plugins](https://github.com/matsengrp/plugins) (the Matsen lab's own bioinformatics-leaning Claude Code plugin). |
| (e) | 5-min `npm install -g @anthropic-ai/claude-code` plus a CLAUDE.md for the repo. |
| (f) | All prompts and code chunks go to Anthropic. **Disqualifying for unpublished patient data without a BAA**; Anthropic's January-2026 Claude for Healthcare offering closes part of that gap but is enterprise-only. |
| (g) | Sycophancy and "honey badger" persistence (Simon Willison's term, [simonwillison.net/2025/May/23/honey-badger/](https://simonwillison.net/2025/May/23/honey-badger/)) — burns tokens to satisfy poorly-scoped prompts. Hidden state in CLAUDE.md is probabilistic, not deterministic ([VILA-Lab/Dive-into-Claude-Code](https://github.com/VILA-Lab/Dive-into-Claude-Code)). |
| (h) | **Best-in-class for individual scientists where data sensitivity allows; do not let it touch protected data.** |

#### Cursor / Windsurf / Copilot Workspace / Codex (2025) / Zed
- **Cursor** and **Windsurf** are commercial IDE forks with strong agent modes; both can route to local models via OpenAI-compatible endpoints, but neither is fully offline (Cursor's docs make this explicit — see [aimultiple.com/local-ai-agent](https://aimultiple.com/local-ai-agent)). **Cursor Notebooks** is one of the few agentic Jupyter solutions in the wild.
- **GitHub Copilot agent mode** + **Copilot Workspace** are mature for boilerplate; the agentic mode is now usable but ties you to GitHub.
- **OpenAI Codex (2025 cloud agent)** is competitive on SWE-bench Verified (top-3 with `gpt-5.2-codex` at 80.0 % per the [Mar-2026 dev.to leaderboard write-up](https://dev.to/rahulxsingh/swe-bench-scores-leaderboard-explained-2026-54of)). Cloud-only.
- **Zed** ships an Assistant panel and is the only mainstream editor with first-class CRDT collaboration; the Assistant supports OpenAI-compatible endpoints including Ollama. Useful for pair-programming sessions in a research lab.

**Notebook handling.** Notebooks are still the weakest spot for every coding agent. Marimo's `marimo pair` skill ([marimo.io/blog/marimo-pair](https://marimo.io/blog/marimo-pair)) is the cleanest 2026 solution: it drops Claude Code (or Codex/OpenCode) inside a *running* reactive notebook session so the agent can read kernel state without context-blowing serialization. **If your lab uses notebooks, this is a meaningful 2026 reason to migrate from Jupyter to marimo (Part 5).**

### 2.2 Autonomous SWE agents and the SWE-bench picture

The April-2026 SWE-bench Verified picture, drawn from the official leaderboard ([swebench.com/verified.html](https://www.swebench.com/verified.html)) and the [awesomeagents.ai April-2026 snapshot](https://awesomeagents.ai/leaderboards/swe-bench-coding-agent-leaderboard/):

- **Closed top:** Claude Opus 4.5 (80.9 %), Claude Opus 4.6 (80.8 %), Gemini 3.1 Pro (80.6 %), GPT-5.2-Codex (80.0 %).
- **Open-source models in agent harnesses:** Kimi K2.5 (~76.8 %), GLM-4.7 (~73.8 %), DeepSeek V3.2 (~73.1 %) per [Likhit Kumar's Medium summary](https://medium.com/@likhitkumarvp/which-local-llm-is-better-a-deep-dive-into-open-source-ai-models-in-2026-benchmarked-b786d6e13384) — these are independent reproductions in `mini-SWE-agent` rather than vendor self-reports.
- **Caveat:** SWE-bench Pro (Scale AI's harder, multi-language, contamination-controlled benchmark) drops the same top models to 46–57 %. Take the 80 % numbers with that grain of salt.
- **OpenHands** ([github.com/All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands), MIT, ~68 k stars) remains the most reproducible open-source SWE-agent scaffold and is what most independent benchmarks use. **SWE-agent** (Princeton) and the minimal **mini-SWE-agent** are the academic reference designs.
- **Devin (Cognition)** — Devin 2.0 sits at ~45.8 % unassisted on SWE-bench Verified per the [awesomeagents leaderboard methodology](https://awesomeagents.ai/leaderboards/swe-bench-coding-agent-leaderboard/), well below the same models running in mini-SWE-agent. Marketing claims should be discounted accordingly.
- **Cline** (~58 k stars) and **Roo Code** (Cline fork, ~22 k) are the dominant OSS VS Code agents; both support local Ollama/LM Studio endpoints ([roocode.com docs](https://docs.roocode.com/advanced-usage/local-models)). **Goose** (Block) is the most "any LLM, including fully local" of the bunch ([github.com/block/goose](https://github.com/block/goose)).

### 2.3 PR-review bots in academic GitHub orgs

- **CodeRabbit** — the most-installed AI reviewer (>2M repos, 13M+ PRs reviewed per [dev.to/heraldofsolace state-of-2026 piece](https://dev.to/heraldofsolace/the-best-ai-code-review-tools-of-2026-2mb3)). Multi-platform (GitHub/GitLab/Bitbucket/Azure DevOps), 40+ linter/SAST integrations, 500+-seat self-hosted tier. **Diff-only** review is its known weakness.
- **Greptile** — full-codebase indexing, **self-hosted in your AWS** option, custom rules in plain English ([greptile.com](https://www.greptile.com)). Catches more deep bugs but produces more noise; a community A/B test put it at 82 % bug detection vs CodeRabbit's 44 %, with the trade-off being signal-to-noise ([qodo.ai/blog/greptile-alternatives](https://www.qodo.ai/blog/greptile-alternatives/)).
- **Sweep AI / Sourcery / Bito / Qodo** — all viable; Sourcery has solid Python/Notebook support. None is meaningfully better than CodeRabbit/Greptile for typical academic Python.
- **Claude Code in GitHub Actions** via `anthropic-ai/claude-code-action` — the cheapest and most flexible "PR reviewer the lab fully controls", and the path I recommend for any repo that already has a CLAUDE.md.
- **Notebook handling.** All review bots remain weak on `.ipynb` diffs. The Sourcery + CodeRabbit combo is the best of a mediocre set; converting notebooks to Marimo's pure-Python format eliminates the problem entirely.

### 2.4 The local-LLM-friendly path

Tested combinations that actually work in April 2026:

- **Aider + Ollama + Qwen2.5-Coder-32B / Qwen3-Coder / DeepSeek-Coder-V3 / Codestral / GLM-4.6-Coder** — see Aider's [Ollama instructions](https://aider.chat/docs/llms/ollama.html) and the [Qwen3 polyglot results](https://aider.chat/2025/05/08/qwen3.html). **Always set `num_ctx`** explicitly; Aider warns that Ollama silently drops context past the default 2 k window. On a single 24 GB consumer GPU (3090/4090), Qwen2.5-Coder-32B at IQ4_XS or Qwen3-Coder-Next-80B-A3B at Q4_K_M are sweet-spot picks; on an 80 GB H100 you can run the larger DeepSeek and GLM variants without quantization.
- **Continue.dev** with the same models; Continue's custom doc-index feature also doubles as a lightweight PaperQA-lite for engineers who already live in VS Code.
- **Cline / Roo Code** with self-hosted **vLLM** or **SGLang** for shared lab use; both support OpenAI-compatible endpoints. The [llama.cpp tutorial #14758](https://github.com/ggml-org/llama.cpp/discussions/14758) walks through plugging Cline into a local llama-server.
- **Hardware budget (April 2026):**
  - A single 24 GB GPU runs ≤32 B-class coders well; expect ~80 % the quality of cloud frontier models on Aider polyglot.
  - One 80 GB H100 runs 70–110 B-class MoE coders comfortably.
  - For full Qwen3-235B or DeepSeek-V4 you need multi-GPU or H200/B200 nodes.

### 2.5 First-hand adoption posts

- **Patrick Mineault (NeuroAI, Amaranth Foundation)** — ["Claude Code for Scientists"](https://www.neuroai.science/p/claude-code-for-scientists), Bluesky-shared via `@patrickmineault.bsky.social` ([linked from his About page](https://xcorr.net/about/)). "*[Claude Code] makes it possible to 1) remain productive and somewhat in the weeds as a senior researcher or PI, and 2) makes it much more feasible to be a solo researcher. … But it also means you can produce wrong results faster than ever before.*" Mineault recommends Snakemake as the orchestrator, true neutral cookiecutter as the project skeleton, and using plan mode aggressively.
- **Simon Willison** (`@simonwillison.net` on Bluesky, [simonwillison.net/tags/claude-code](https://simonwillison.net/tags/claude-code/)) is the most prolific public log of agentic-coding workflows. February-2026: "*Most people's mental model of Claude Code is that 'it's just a TUI' but it should really be closer to 'a small game engine'.*" His Claude Skills write-up ([Oct-2025 essay](https://simonwillison.net/2025/Oct/16/claude-skills/)) is the canonical reference for the SKILL.md pattern.
- **Hamel Husain** ([hamel.dev](https://hamel.dev/)) — a former Airbnb/GitHub ML engineer whose evals-first writing has become the de facto standard for LLM-product engineering, including coding agents. His ["Field Guide to Rapidly Improving AI Products"](https://hamel.dev/blog/posts/field-guide/) and ["Revenge of the Data Scientist"](https://hamel.dev/blog/posts/revenge/) are required reading before deploying any of the tools above into a lab pipeline.
- **Anthropic's own engineering team** — ["Long-running Claude for scientific computing"](https://www.anthropic.com/research/long-running-Claude) is the reference write-up for using Claude Code with SLURM, including the CHANGELOG.md "lab notes" pattern many labs are now copying.

### 2.6 Editorial — opinionated default stacks

**For an individual scientist on a laptop:** **Claude Code** as the daily driver, **Cursor** as the GUI fallback when you want point-and-click, and **Aider + Ollama + Qwen2.5-Coder-32B** as the offline fallback for sensitive data and travel. Write a project-specific `CLAUDE.md` (and a sibling `AGENTS.md` to cover Cursor/Codex) following Patrick Mineault's pattern: pin folder structure, mandate Snakemake/uv/ruff, demand commit-and-push after every meaningful unit, and instruct the agent to maintain a `CHANGELOG.md` of failed approaches. Keep one terminal pane on `simonwillison.net` for the weekly state-of-the-art update; the field changes monthly.

**For a shared lab repo with junior contributors:** **Claude Code in GitHub Actions** (via `anthropic-ai/claude-code-action`) for autonomous review and code-fix proposals, **CodeRabbit** as the second-opinion linter on every PR, a **CLAUDE.md / AGENTS.md** committed to the repo enforcing the lab's coding-style and reproducibility rules, and **pre-commit + ruff + nbqa** as the deterministic guardrail. Self-hosted **Greptile** is the upgrade path if the institution's privacy office vetoes CodeRabbit. **Do not** make Devin or Cursor "the" agent for a shared repo — both are too proprietary for institutional repos that may outlive a vendor.

### Part 2 comparison table

| Tool | Hosting | Local-LLM | License | Lab fit |
|---|---|---|---|---|
| Claude Code | SaaS API | partial | proprietary | adopt for individuals |
| Cursor / Windsurf | SaaS+local LLM | partial | proprietary | optional GUI |
| Aider | local | yes | Apache-2.0 | adopt as offline fallback |
| Continue.dev | local | yes | Apache-2.0 | adopt for VS Code |
| Cline / Roo Code | local | yes | Apache-2.0 | adopt if you live in VS Code |
| Goose (Block) | local | yes (any LLM) | Apache-2.0 | best fully-local agent |
| OpenHands | self-host | yes | MIT | research-grade autonomous agent |
| SWE-agent / mini-SWE-agent | self-host | yes | MIT | benchmarking + reference design |
| Devin | SaaS | no | proprietary | skip |
| CodeRabbit | SaaS / self-host (≥500 seats) | n/a | proprietary | adopt as PR reviewer |
| Greptile | SaaS / self-host AWS | yes (BYO LLM) | proprietary | adopt for sensitive repos |
| Sourcery | SaaS | n/a | proprietary | useful Python/notebook addition |
| Zed Assistant | local + LLM | yes | GPL | useful for collaborative pairing |

---

## Part 3 — Bureaucracy and Documentation Automation

### 3.1 Git hygiene with AI

- **OpenCommit** ([github.com/di-sukharev/opencommit](https://github.com/di-sukharev/opencommit)) is the most feature-rich AI commit-message tool and supports **Ollama**, Anthropic, OpenAI, Azure, Gemini and DeepSeek. The `oco hook set` pattern installs a `prepare-commit-msg` git hook so it runs on every commit without effort. Active package on npm.
- **aicommits** (Nutlope) is the leaner alternative; minimal config, OpenAI-only by default ([dev.to comparison](https://aicoolies.com/comparisons/opencommit-vs-aicommits)).
- **aicommit2** and bespoke shell scripts (e.g. [Karpov's git-aicommit Medium recipe](https://medium.com/@karpulix/use-git-aicommit-git-commit-powered-by-ai-1d717f9abd32)) are valid for engineers who prefer a 50-line bash file over a node dependency.
- **commitizen / commitlint / husky** remain the deterministic baseline. Pair OpenCommit (for the suggested message) with commitlint (for the deterministic policy check).

**Verdict:** **OpenCommit + Ollama + Mistral-7B / Qwen3-4B** is the reference local-LLM-friendly setup for a privacy-sensitive lab. Wire it via `pre-commit` so contributors cannot forget. Cost: zero per commit; ~6 GB VRAM if you want it instant.

### 3.2 Living documentation

- **Sphinx / MkDocs / Quarto / JupyterBook** are the doc-as-code substrates; **Quarto** is the right default for mixed-language scientific labs (it speaks R, Python, Julia and Observable in one document and renders beautifully on Read the Docs / GitHub Pages).
- **Mintlify Doc Writer**, **Trelent**, **DocuWriter.ai**, **Cursor `/docs`** and **Codeium docs** all generate docstrings; quality is mediocre for scientific code, where the agent rarely understands domain conventions. The pragmatic pattern is **Claude Code with a project-level `docs` skill** that knows your team's docstring style.
- **Read the Docs** has had AI-augmented build hooks since 2024; in practice most labs use a CI step that runs Claude Code or `aider` in scripted mode against changed files.
- **`semantic-release` / `release-please`** auto-generate changelogs from Conventional Commits — making OpenCommit's output the upstream input.
- **Repomix** ([github.com/yamadashy/repomix](https://github.com/yamadashy/repomix), MIT) packs an entire repo into a single AI-friendly XML file with token counts, secret-scanning and tree-sitter compression. It is the simplest way to feed an existing repo to Claude/Codex/Aider for documentation generation. Adopt as a 1-minute install for any lab.

### 3.3 Project scaffolding for reproducibility

The April-2026 "good scientific Python project" has converged on:

- **uv** (Astral, [docs.astral.sh/uv](https://docs.astral.sh/uv)) — Rust-based 10–100× faster pip/pip-tools/virtualenv replacement, with universal lockfiles and `uv tool install` for global tools. **The new default**, replacing pip + pip-tools + pyenv + poetry combos.
- **pixi** (prefix.dev, [pixi.prefix.dev](https://pixi.prefix.dev/)) — conda-ecosystem package manager with a lockfile and built-in tasks. Particularly strong for **bioinformatics** because it pulls from bioconda + conda-forge, integrates with `uv` for PyPI extras, and avoids the conda-defaults licensing issue (see [Edmund Miller's post](https://edmundmiller.dev/posts/pixi-bioinformatics/) and [Xiaofei Carl Zang's switching guide](https://x-zang.github.io/blog/switch-from-conda-to-pixi/)). The reference choice for any lab with compiled tools (samtools, STAR, DESeq2, Nextflow) in the stack.
- **cookiecutter / copier** — for repo templating; cookiecutter-data-science v2 ("ccds") shipped in 2024.
- **pre-commit + ruff + nbqa + commitlint** — the deterministic guardrail.
- **Quarto + JupyterBook** — for docs/preprints.
- **DVC** for any dataset above 1 GB; **MLflow / Weights & Biases / Aim / CometML** for experiment tracking (see 3.4).

**Encoding the recipe in a CLAUDE.md / AGENTS.md / SKILL.md.** The 2026 pattern is to commit a project-level `CLAUDE.md` that says "use `uv add` not `pip install`, format with ruff, lint with mypy, pin every dataset with DVC, write tests in pytest, log experiments to MLflow, commit and push after every meaningful unit." Real examples:

- Anthropic's own ["Long-running Claude for scientific computing"](https://www.anthropic.com/research/long-running-Claude) reference CLAUDE.md / CHANGELOG.md pair.
- **VoltAgent's awesome-claude-code-subagents** ([github.com/VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents)) — 100+ subagents including a `scientific-literature-researcher` template.
- **matsengrp/plugins** ([github.com/matsengrp/plugins](https://github.com/matsengrp/plugins)) — Erick Matsen's lab plugin with `snakemake-pipeline-expert`, `clean-code-reviewer`, `pdf-proof-reader` and a `scientific-tex-editor`.
- **GPTomics/bioSkills** and **K-Dense-AI/scientific-agent-skills** — open skill libraries packaging bioinformatics, cheminformatics and lab-automation patterns. Useful as starting points; **review them carefully** before installing because they are community-curated and not security-audited.

### 3.4 Experiment tracking

- **MLflow** is the OSS workhorse and works fine offline.
- **Weights & Biases** is the gold-standard SaaS for ML; CometML and Aim are open alternatives. **Aim** is the most "self-hostable, no telemetry" of the bunch.
- **DVC** for data and pipeline versioning.
- **Hugging Face `ml-intern`** ([github.com/huggingface/ml-intern](https://github.com/huggingface/ml-intern), released April 21, 2026) is the reference design for "the agent records its own experiment metadata as it runs". It uses **Trackio** for OSS experiment tracking, auto-launches HF Jobs, and reads its own eval outputs to diagnose failures. The launch-day claim of pushing a Qwen3-1.7B from ~10 % to 32 % on GPQA in 10 hours, beating Claude Code's 22.99 % on the same task ([MarkTechPost summary](https://www.marktechpost.com/2026/04/21/hugging-face-releases-ml-intern-an-open-source-ai-agent-that-automates-the-llm-post-training-workflow/)), is **vendor-self-reported** on a benchmark Hugging Face designed; treat as illustrative until independent reproduction. The architecture — bounded agentic loops, doom-loop detection, ContextManager, ToolRouter, sandboxed execution — is the design pattern worth copying. (Deep dive lives in Prompt B Part 8.)

### 3.5 First-hand adoption posts

- **Edmund Miller (nf-core / Element Biosciences, applied genomics)** — ["Simplify your bioinformatics workflow with Pixi"](https://edmundmiller.dev/posts/pixi-bioinformatics/): "*I recently started using Pixi from prefix.dev. It's been really nice. I want to forget about a package manager. Pixi let's me do that.*" Includes a copy-paste setup for nextflow/rclone via `pixi global install`.
- **Xiaofei Carl Zang (computational biology)** — ["Switching from conda to pixi"](https://x-zang.github.io/blog/switch-from-conda-to-pixi/), with concrete advice for labs already on bioconda and a no-marketing comparison.
- **Patrick Mineault** — same ["Claude Code for Scientists"](https://www.neuroai.science/p/claude-code-for-scientists) post: "*Give Claude rails with folder structure. My true neutral cookiecutter is a decent starting point … Use an orchestrator. Your codebase will grow much faster than when you write things by hand. … I'm using Snakemake, which is popular in bioinformatics.*"
- **Simon Willison** — Bluesky thread on Claude Skills: "*A skill is a Markdown file telling the model how to do something, optionally accompanied by extra documents and pre-written scripts that the model can run*" ([simonwillison.net/2025/Oct/16](https://simonwillison.net/2025/Oct/16/claude-skills/)).

### 3.6 Editorial — the minimum-viable bureaucracy stack

Before any lab adopts an autonomous coding agent, insist on this exact stack: **`uv` (and `pixi` if there are compiled tools)**, **`pre-commit` with `ruff` + `nbqa` + `commitlint`**, **Conventional Commits** generated by **OpenCommit + Ollama** as a `prepare-commit-msg` hook, a project-level **CLAUDE.md / AGENTS.md** that pins folder structure and reproducibility rules and tells the agent to maintain a CHANGELOG.md, **DVC** for any dataset over 1 GB, **MLflow or Aim** for experiment tracking, and **Quarto** for docs. Total install time: under one engineer-day for a fresh repo, two days for a retrofit. None of this is novel — but precisely *because* it is unsexy, it is what differentiates labs whose agentic coding produces compounding results from labs whose agentic coding produces a high-velocity mess.

The second editorial point: **commit your CLAUDE.md / AGENTS.md / SKILL.md to the repo and treat it as code**. It is the lab's enforceable "constitution" and it is the only artefact that survives the next agent generation. Keep it short, version it like a paper, and let the agent itself propose changes via PR.

### Part 3 comparison table

| Tool | Hosting | Local-LLM | License | Lab fit |
|---|---|---|---|---|
| OpenCommit | local | yes (Ollama) | MIT | adopt now |
| aicommits | local | partial | MIT | viable alt |
| Repomix | local | n/a | MIT | adopt as 1-day win |
| uv | local | n/a | MIT/Apache | adopt now |
| pixi | local | n/a | BSD-3 | adopt for bioinformatics |
| cookiecutter / copier | local | n/a | BSD/MIT | adopt now |
| Quarto | local | n/a | MIT | default doc engine |
| pre-commit + ruff | local | n/a | MIT | non-negotiable |
| DVC | local + cloud | n/a | Apache-2.0 | adopt for data ≥1 GB |
| MLflow | local | n/a | Apache-2.0 | default tracker |
| Aim | local | n/a | Apache-2.0 | privacy-first alt |
| Weights & Biases | SaaS | n/a | proprietary | only if grant-funded |
| HF `ml-intern` | self-host | yes | Apache-2.0 | watch / pilot Q3 |
| Anthropic Skills (CLAUDE.md / SKILL.md) | spec | n/a | open spec | adopt the pattern |
| matsengrp/plugins, VoltAgent subagents, K-Dense scientific-agent-skills | local | yes | MIT | mine for templates |

---

## Part 4 — Meeting Recording, Transcription, Diarization, Summarization

### 4.1 ASR engines (April 2026)

The Hugging Face Open ASR Leaderboard ([huggingface.co/spaces/hf-audio/open_asr_leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) and the [Oct-2025 paper arXiv:2510.06961](https://arxiv.org/html/2510.06961v3)) is the only reproducible cross-vendor ASR comparison. Selected averaged WER (lower is better) on English short-form:

| Model | License | Avg WER | RTFx | Multilingual |
|---|---|---|---|---|
| NVIDIA Canary-Qwen 2.5B | NV community | 5.63 | — | en |
| IBM Granite Speech 3.3 8B | Apache-2.0 | 5.85 | — | en+ |
| NVIDIA Parakeet-TDT 0.6B v3 | CC-BY-4.0 | 6.32 | 3,330 | 25 EU langs |
| Mistral Voxtral Small 24B | Apache-2.0 | 6.62 | 54 | 8 |
| NVIDIA Canary-1B v2 | NV community | 7.15 | 749 | 25 |
| Distil-Whisper Large v3.5 | MIT | 7.21 | 202 | en |
| OpenAI Whisper Large v3 | MIT | 7.44 | 146 | 99 |
| Whisper Large v3 Turbo | MIT | ~8.0 | ~600 | 99 |
| OpenAI Whisper Large v3 (in faster-whisper / CTranslate2) | MIT | ~7.5 | ~500 | 99 |

Practical reading:
- **Whisper-large-v3-turbo** is still the best generalist for a 5–25-person lab in a multilingual European setting (Dutch, German, French, English at one meeting). The MIT licence and 99-language coverage matter.
- **Parakeet-TDT-0.6B-v3** is the right choice if your audio is mostly one of 25 European languages, you have NVIDIA GPUs, and you need throughput — ~25–30× Whisper at the same accuracy ([arunbaby.com comparison](https://www.arunbaby.com/speech-tech/0073-whisper-vs-parakeet-asr-decision/)). Note that Parakeet's strong English numbers are *English-only*; v3 is the multilingual variant and trades a bit of English accuracy for breadth.
- **faster-whisper** ([github.com/SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper)) and **whisper.cpp** are still the right CTranslate2 / C++ runtimes; Speechmatics is the high-end commercial option and refuses to publish RTFx for fair comparison.
- **Configuration matters more than model choice** for production: an [E2E Networks L4 study](https://www.e2enetworks.com/blog/benchmarking-asr-models-nvidia-l4-parakeet-whisper-nemotron) showed SDPA attention gives Whisper a 1.8× free throughput improvement most deployments don't enable, and Whisper with `chunk=10s` causes a 3.5 % absolute WER regression — a hidden trap.

### 4.2 Diarization

- **pyannote.audio 3.1 / community-1** ([huggingface.co/pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)) is the most accurate open pipeline; the **HuggingFace gating** (you must accept the model's terms) is the catch and breaks unattended Docker deploys. The new `pyannote/speaker-diarization-community-1` removes onnxruntime and runs in pure PyTorch.
- **NVIDIA NeMo Sortformer / Sortformer v2 / Sortformer v2-streaming** ([emergentmind sortformer overview](https://www.emergentmind.com/topics/sortformer-model)) is the fastest streaming-capable open diarizer (RTF 214× audio length per the [Sept-2025 benchmark arXiv:2509.26177](https://arxiv.org/html/2509.26177v1)) but caps at ~4 speakers in v1.
- **Independent benchmark, Sept 2025:** PyannoteAI commercial = 11.2 % DER, DiariZen = 13.3 %, Sortformer v2-streaming competitive on 2-speaker audio but degrades at 5+ speakers. **For a 6-person lab meeting on Zoom audio, expect 12–15 % DER** with pyannote 3.1; passable but speaker labels need human cleanup.
- **Practical advice:** if you know how many people are in the room, *always* pass `num_speakers` to pyannote — it is the single biggest accuracy lever ([Neosophie experiment report](https://neosophie.com/en/blog/20260223-diarization)).

### 4.3 Self-hosted end-to-end stacks

- **Meetily** ([github.com/Zackriya-Solutions/meetily](https://github.com/Zackriya-Solutions/meetily)) — Tauri/Rust desktop app, captures system + mic audio without a meeting bot, runs whisper.cpp or Parakeet locally, summarizes via Ollama. MIT, very actively developed; Community Edition free, Pro tier $10/user/month. **The closest 2026 thing to "Otter, but fully on-prem"**, Windows + macOS only (Linux source-build).
- **Whishper** ([github.com/pluja/whishper](https://github.com/pluja/whishper)) — Docker-Compose multi-user web UI for Whisper transcription with subtitle export. No summarization; purely transcription. Good for shared lab "drag-and-drop file → transcript" service.
- **Speaches** ([github.com/speaches-ai/speaches](https://github.com/speaches-ai/speaches), formerly faster-whisper-server) — OpenAI-compatible STT/TTS server. The right backend if you want a single endpoint that Open WebUI, LiteLLM, Obsidian, Home Assistant and custom code can all hit.
- **Speakr** — Docker stack with whisper-ASR + diarization and an Obsidian-export workflow ([XDA write-up](https://www.xda-developers.com/this-self-hosted-tool-turns-audio-into-podcast-style-obsidian-notes/)).
- **whisper-obsidian-plugin** ([github.com/nikdanilov/whisper-obsidian-plugin](https://github.com/nikdanilov/whisper-obsidian-plugin)) and **obsidian_plugin_AI_meeting_notes** ([github.com/tsheil/obsidian_plugin_AI_meeting_notes](https://github.com/tsheil/obsidian_plugin_AI_meeting_notes)) are the two best Obsidian-integrated plugins; the latter explicitly ships dual-channel mic-and-system-audio capture and Ollama post-processing.
- **Memos (Tencent)**, **Hyperion**, **Bonsai**, **Subtitle Edit + Whisper** are all viable; none has reached the Meetily / Whishper level of polish for lab use.

### 4.4 The summarization layer

The lab pattern that works: a small Python script that takes a transcript + diarized speaker labels and runs three sequential prompts (decisions, action items, lab-meeting minutes), each producing markdown that is appended to an Obsidian vault. Meetily ships this design as a default. The Obsidian AI Meeting Notes plugin builds the same on top of any local LLM CLI. There is no published peer-reviewed "lab meeting summarization" prompt as of April 2026 [unable to verify]. The most-cited recipe is Meetily's own ([dev.to/zackriya/local-meeting-notes-with-whisper-transcription-ollama-summaries-gemma3n-llama-mistral](https://dev.to/zackriya/local-meeting-notes-with-whisper-transcription-ollama-summaries-gemma3n-llama-mistral--2i3n)).

### 4.5 Privacy, consent, and IRB

The cultural and IRB questions are not technical: who consents (every trainee, including those who will join later); where the audio is stored (lab-controlled disk, encrypted at rest with LUKS or FileVault); how long it is retained (90 days is a defensible default; transcripts and summaries longer); whether transcripts can ever be shared with cloud LLMs (no, by default — that is the whole point of going local). Published lab policies on this are still rare; the Allen Institute and FutureHouse have public ethics statements but not detailed lab-meeting recording policies as of April 2026 [unable to verify a published policy that names the recording stack]. **A two-paragraph lab policy committed to your handbook plus a one-page consent form is the minimum bar.** Do not record meetings that contain unconsented patient identifiers, full stop.

### 4.6 First-hand adoption posts

- **James Ravenscroft** (`@jamesravey.bsky.social` / [brainsteam.co.uk](https://brainsteam.co.uk/2025/4/6/adding-voice-to-selfhosted-ai/)) — "Adding Voice to your self-hosted AI Stack": detailed walk-through of Speaches + LiteLLM + Open WebUI on a single 12 GB RTX 3060, with Piper/Kokoro TTS. The most practical "Friday-afternoon-project" template for a lab.
- **Zackriya / Meetily team** ([dev.to author Zackriya](https://dev.to/zackriya)) — multi-post series on local Whisper + Ollama for meeting notes; covers the v0.0.5 Docker stability work and the swap to Parakeet.
- I could not locate a named PI-authored Bluesky thread that specifically describes a fully on-prem Whisper-based **lab-meeting** workflow as of April 2026, after searches across "Bluesky lab meeting Whisper", "PI Otter Granola lab use", and "obsidian Whisper lab meeting". **No first-hand PI adoption post located on Bluesky after three different searches.** The closest analogues are the engineer-authored Ravenscroft post above and Meetily's tutorial series.

### 4.7 Editorial — the Friday-afternoon stack

Buy or repurpose one workstation with a single **NVIDIA RTX A6000 (48 GB)** or a **4090 (24 GB)** — either works; the A6000 lets you run summarization and ASR concurrently without juggling. Install **Speaches** (Docker), **pyannote-audio 3.1** (with `num_speakers` set per meeting), **WhisperX** for word-level alignment, **Ollama** running **GLM-4.7-Air** or **Qwen3-30B-A3B-Instruct** for summarization, and **LiteLLM** as the front-door router. Wire it as: a shared dropbox folder on the lab NAS → a `cron` or `systemd.timer` that picks up new audio every 15 minutes → Whisper-large-v3-turbo for transcription → WhisperX for alignment → pyannote for diarization → a three-stage summarization prompt → markdown into the lab's Obsidian vault under `Meetings/{YYYY-MM-DD}-{topic}.md`. End-to-end install: one motivated engineer, two days; ~1 GB of GPU RAM headroom for everything except Whisper-turbo + 30B summary running at the same time, in which case 48 GB is necessary.

The political/IRB layer is the harder part. Write a one-page policy: who consents, where the audio lives, when it is purged, who can read summaries. Make consent re-recurring (every six months) so trainees who joined later are not silently swept in. Treat the lab manager and the IRB liaison as your real customers; the engineer-time is the cheap part.

### Part 4 comparison table

| Tool | Hosting | Local-LLM | License | Lab fit |
|---|---|---|---|---|
| Whisper Large v3 / v3-turbo | local | n/a (ASR) | MIT | default ASR |
| faster-whisper | local | n/a | MIT | default runtime |
| WhisperX | local | n/a | BSD-4 | default for word-alignment |
| Distil-Whisper Large v3.5 | local | n/a | MIT | English laptop fallback |
| Parakeet-TDT 0.6B v3 | local | n/a | CC-BY-4.0 | adopt if NVIDIA GPU + EU langs |
| NVIDIA Canary-Qwen 2.5B | local | n/a | NV community | top accuracy, English |
| pyannote 3.1 / community-1 | local | n/a | MIT (model gated) | default diarizer |
| NeMo Sortformer v2 | local | n/a | Apache-2.0 | adopt for streaming |
| Meetily | self-host (desktop) | yes (Ollama) | MIT | adopt for Win/macOS users |
| Whishper | self-host (Docker) | n/a | MIT | adopt for shared transcription |
| Speaches | self-host (Docker) | yes | MIT | OpenAI-compatible backend |
| Char | self-host (desktop) | yes (Apple ANE) | GPL | macOS-only alt |
| Otter / Fireflies / Granola / tl;dv | SaaS | no | proprietary | skip for sensitive data |
| Speechmatics | SaaS | no | proprietary | only for grant-funded high-accuracy ASR |

---

## Part 5 — Enhancing Journal Clubs with Interactive Code Views

### 5.1 Reactive notebook tech

#### Marimo
- **What:** Reactive Python notebook stored as pure `.py`, deployable as **WASM static HTML** via `marimo export html-wasm` ([docs.marimo.io/guides/wasm](https://docs.marimo.io/guides/wasm/)). 20 k+ stars, Apache-2.0, very actively developed, NumFOCUS-affiliated.
- **WASM caveats:** 2 GB browser memory cap, no PDB, no threading/multiprocessing, packages limited to those with pure-Python wheels on Pyodide (NumPy, SciPy, scikit-learn, pandas, polars, duckdb are in; PyTorch is not). For most journal-club purposes, this is fine.
- **AI-native:** The April-2026 `marimo pair` skill ([marimo.io/blog/marimo-pair](https://marimo.io/blog/marimo-pair)) drops Claude Code/Codex/OpenCode inside a *running* notebook session — the cleanest agent-notebook integration in the field.
- **Verdict:** **Best-in-class for "share an interactive paper exploration as a static URL". Adopt.**

#### Pluto.jl
- **What:** The original reactive notebook; Julia-native ([plutojl.org](https://plutojl.org)). Reactive cells, deterministic execution, great pedagogy.
- **Verdict:** **The right choice for a Julia journal club**; for Python-first labs, Marimo is the descendent that fits.

#### Observable Framework
- **What:** Static-site generator for JS reactive dataviz documents ([observablehq.com/framework](https://observablehq.com/framework)). MIT, actively developed.
- **Verdict:** Best when the paper is fundamentally about visualization rather than scientific computation; can host Pyodide cells for hybrid Python/JS exploration.

#### Quarto (interactive)
- **What:** Pandoc-based scientific publishing with optional **Pyodide** (Python-in-browser via [coatless-quarto/pyodide](https://github.com/coatless-quarto/pyodide)) and **webR** backends, unified by the **Quarto Live** extension ([r-wasm/quarto-live](https://github.com/r-wasm/quarto-live)). Renders to HTML, reveal.js slides, books, websites.
- **Verdict:** **The right default for mixed-language labs (R + Python + Julia)**; the only one that gives you a "papers, slides, web app" trio from one source.

#### Jupyter + JupyterLite + Binder
- JupyterLite gives you static-WASM Jupyter; **Binder** gives you ephemeral cloud notebooks. Both work, but Marimo and Quarto-Pyodide produce smaller, faster bundles for journal-club use.

### 5.2 One-click paper demos

- **Hugging Face Spaces** ([huggingface.co/spaces](https://huggingface.co/spaces)) is the de-facto venue; the [arXiv↔Spaces integration](https://huggingface.co/blog/arxiv) puts a "Demos" tab on every arXiv paper page.
- **Gradio / Streamlit** are the SDKs; Gradio is the right default for Spaces (5-min build).
- **Replicate / Modal / Sieve / Beam** are the right backends when a demo needs serious GPU.

Real research-lab demos worth pointing students at (sampled from the SpacesExamples organization and arxiv↔Spaces): the **AnimeGANv2** demo (popular template), Microsoft's **DiT Document Layout Analysis** Space, the **DocFormer** Space linked to Microsoft's LayoutLM, and the protein-structure demos showcased on the [arXiv blog post](https://blog.arxiv.org/2022/11/17/discover-state-of-the-art-machine-learning-demos-on-arxiv/). I cannot point to a single canonical "top scientific Spaces" registry as of April 2026 [unable to verify a curated registry beyond `SpacesExamples`]. The pragmatic move is to navigate the "Demo" tab on arXiv pages of papers you actually plan to discuss.

### 5.3 LLM-augmented paper exploration

- **PaperQA2 + a code retriever** is the bottom-up approach: clone the paper repo, ingest the paper PDF + the README + key source files, then ask "where in the code does Equation 4 happen?" against a local 30B coder.
- **Cursor or Claude Code over a cloned paper repo** is the top-down approach. Patrick Mineault's ["Claude Code for Scientists"](https://www.neuroai.science/p/claude-code-for-scientists) is the canonical recipe; the Anthropic ["long-running Claude"](https://www.anthropic.com/research/long-running-Claude) Boltzmann-solver case study is the most ambitious public example.
- **Repomix** ([repomix.com](https://repomix.com/)) packs the paper's repo into a single LLM-friendly file in seconds — the simplest way to make any LLM "read" a paper repo.
- **Paper2Code / PaperCoder** ([arXiv:2504.17192](https://arxiv.org/abs/2504.17192), [github.com/going-doer/Paper2Code](https://github.com/going-doer/Paper2Code)) is a multi-agent framework that takes a paper PDF and generates a code repository. It runs against PaperBench and DeepSeek-Coder-V2 by default. The reported author-evaluations are positive but the system has no peer-reviewed independent reproduction yet [non-peer-reviewed preprint, single-team evaluation]. **Useful as a "starter scaffold for a paper that ships no code", not as a trustworthy reimplementation.**
- **AutoP2C** ([arXiv:2504.20115](https://arxiv.org/pdf/2504.20115)) extends Paper2Code to multimodal content (figures, equations, tables) — same caveats.
- **Marimo's "implement a paper" skill** ([marimo.io/blog/marimo-pair](https://marimo.io/blog/marimo-pair)) ships a structured prompt for "give an agent a link to a paper and have it generate an educational notebook"; it powered marimo's [molab notebook competition with alphaXiv](https://marimo.io/pages/events/notebook-competition).

**Honest caveat.** The "AI Scientist" line of work (Sakana, [sakana.ai/ai-scientist](https://sakana.ai/ai-scientist/)) and its open-source derivatives received an [independent evaluation arXiv:2502.14297](https://arxiv.org/abs/2502.14297) showing that 42 % of generated experiments fail with coding errors, novelty assessments are weak, citation quality is poor (median 5 references per paper, only 5/34 from 2020+), and several manuscripts contain hallucinated numerical results. The same skepticism applies, in proportion, to Paper2Code and any "regenerate this paper" agent. Use them to *learn* a paper, not to *trust* the regenerated implementation.

### 5.4 First-hand adoption posts

- **The marimo team blog** ([marimo.io/blog](https://marimo.io/blog)) regularly publishes journal-club-style notebook walk-throughs; the **alphaXiv ↔ marimo notebook competition** ([marimo.io/pages/events/notebook-competition](https://marimo.io/pages/events/notebook-competition)) explicitly asks researchers to "*pick a paper and build a notebook that brings its core idea to life*" — the closest thing to a public "we replaced our journal club slides with a live notebook" recipe.
- **Antonin Peronnet's [Sketch Vectorization marimo notebook](https://marimo.io/pages/events/notebook-competition)** is the marimo team's reference example: "*not only re-implements the paper but also adds novel extensions such as a CNN with synthetic data augmentation.*"
- **Quarto Live launch posts** ([tidyverse.org/blog/2024/10/quarto-live-0-1-1](https://tidyverse.org/blog/2024/10/quarto-live-0-1-1/)) are the canonical reference for the educational-tutorial pattern; many epidemiology and statistics PIs now use Quarto-Live instead of slides for journal clubs.
- I could not locate a named PI Bluesky thread specifically titled "we replaced our journal club with a Marimo notebook" after three searches. **No first-hand PI Bluesky post located.** The closest is the marimo team's own posts and academic econometrics/biostatistics labs that have switched to Quarto-based interactive tutorials.

### 5.5 Editorial — a concrete journal-club format for next semester

Adopt the following format for one semester and review:

1. **Two weeks before the meeting**, the presenter clones the paper's repo and runs **Repomix** on it. They open a new **Marimo** notebook (`marimo edit --sandbox paper.py`), import key functions from the paper repo, and write three "what if" cells with reactive sliders / dropdowns binding to the most important parameter.
2. **One week before**, the presenter runs **Claude Code** (or **Aider + Qwen3-Coder** if data is sensitive) on the cloned repo with a prompt like: *"Read this paper and the repo. Surface 3 questions an audience could ask that change the result, and add 3 small reactive widgets to `paper.py` that let the audience answer those questions live."* The presenter reviews the suggestions, keeps the good ones, and writes a 200-word "context" cell.
3. **Day-of**, the presenter runs `marimo export html-wasm paper.py -o paper.html` and pushes to GitHub Pages. Every audience member opens the URL in their browser and can fork-and-tweak in their own tab without installing Python.
4. **During the meeting (45 min total),** 10 min of context, 20 min of paper-walkthrough with everyone tweaking sliders and posting screenshots in chat, 15 min of discussion.
5. **After the meeting**, the notebook lives in the lab's `journal-club/` GitHub repo as a permanent searchable artefact. The Whisper-based meeting transcription pipeline from Part 4 captures the discussion and saves it next to the notebook.

The total presenter prep time is ~3 hours instead of the ~5 hours of slide-making it replaces, and the artefact is reusable for teaching, recruitment, and PI grant prep. For the first semester, run only one or two papers this way; the format is high-leverage but learning the toolchain takes a presenter ~2 attempts to internalize. **Insist on Marimo over Jupyter for new journal-club notebooks; Quarto-Live with `webR` if your lab is R-first.**

### Part 5 comparison table

| Tool | Hosting | Local-LLM | License | Lab fit |
|---|---|---|---|---|
| Marimo | local + WASM | yes (marimo pair) | Apache-2.0 | adopt now |
| Pluto.jl | local + WASM (PlutoSliderServer) | n/a | MIT | adopt for Julia labs |
| Observable Framework | local + static | n/a | ISC | adopt for dataviz-heavy papers |
| Quarto (Pyodide / webR) | local + static | n/a | MIT | default for mixed-language labs |
| Jupyter + JupyterLite + Binder | local + WASM + cloud | n/a | BSD-3 | legacy / fallback |
| Hugging Face Spaces | SaaS | partial | proprietary host | adopt for paper demos |
| Gradio / Streamlit | local | n/a | Apache-2.0 / Apache-2.0 | adopt as demo SDKs |
| Replicate / Modal | SaaS | n/a | proprietary | for GPU demos |
| PaperQA2 + code retrieval | self-host | yes | Apache-2.0 | adopt for "where in the code is Equation 4?" |
| Repomix | local | n/a | MIT | adopt as 1-day win |
| Paper2Code / PaperCoder | self-host | yes | open | watch — non-peer-reviewed |
| Cursor over paper repo | SaaS+local | partial | proprietary | option |
| Claude Code on paper repo | SaaS API | partial | proprietary | option |
| Idyll / Distill.pub | static | n/a | open | inspiration / lineage |

---

## Mini comparison matrix for Parts 1–5

Sorted by Part, then by Lab fit (descending). "Local-LLM?" = first-class support for Ollama/vLLM/llama.cpp/OpenAI-compatible endpoints. "Lab fit" is a 1–5 score with 5 = adopt now lab-wide, 1 = skip.

| Tool | Part(s) | Hosting | Local-LLM? | License | Maturity (Apr 2026) | Lab fit (1–5) | Best for | Watch out for |
|---|---|---|---|---|---|---|---|---|
| PaperQA2 | 1 | self-host | yes | Apache-2.0 | mature | 5 | grounded RAG over lab PDFs | "superhuman" claim is small-n self-report |
| Scholar Inbox | 1 | SaaS | n/a | free academic | mature | 5 | personalized daily paper feed | preferences live on vendor servers |
| Docling | 1 | self-host | n/a | Apache-2.0 | mature | 5 | default PDF→markdown for science | slower than Marker on CPU |
| Marker | 1 | self-host | n/a | model weights CC-BY-NC-SA | mature | 4 | fastest PDF→markdown | NC weights restrict commercial use |
| Qwen3-Embedding | 1, 2 | self-host | n/a | Apache-2.0 | mature | 5 | default embedding model | English/Chinese-skewed |
| BGE-M3 | 1 | self-host | n/a | MIT | mature | 5 | hybrid retrieval | older than Qwen3 |
| Local Deep Research | 1 | self-host | yes | MIT-ish | active | 4 | privacy-first deep-research clone | benchmark numbers self-reported |
| Khoj | 1 | self-host | yes | AGPL | active | 4 | second-brain over PDFs/Markdown | AGPL may bother some institutions |
| MinerU | 1 | self-host | n/a | AGPL-3.0 | active | 4 | math/non-English document parsing | AGPL |
| ColPali | 1 | self-host | n/a | Gemma research | active | 3 | figure/table-heavy retrieval | OCR pipelines generalize better to unseen docs |
| STORM | 1 | self-host | yes (DSPy) | MIT | mature | 3 | first-draft surveys | Wikipedia-style, weak at grounded QA |
| LangChain open_deep_research | 1 | self-host | yes | MIT | active | 3 | reference deep-research design | heavyweight LangGraph dep |
| Open WebUI + research pipes | 1, 4 | self-host | yes | OWUI BSD-style | active | 3 | shared lab chat front-end | research pipes are alpha |
| Undermind / Ai2 Paper Finder / Crow | 1 | SaaS | n/a | mixed | mature | 3 | cross-check searches | queries leave premises |
| GPT Researcher | 1 | self-host | yes | Apache-2.0 | active | 3 | open-source deep research | no recent independent benchmark |
| Claude Code | 2, 3, 5 | SaaS API | partial (router) | proprietary | mature | 5 | individual scientist daily driver | not for unpublished patient data |
| Aider | 2 | local | yes | Apache-2.0 | mature | 5 | offline pair-programmer | needs careful Ollama context config |
| Continue.dev | 2 | local | yes | Apache-2.0 | mature | 5 | VS Code local assistant | mediocre out-of-box rules |
| Cline / Roo Code | 2 | local | yes | Apache-2.0 | mature | 4 | full-feature VS Code agents | quality depends on connected model |
| Goose (Block) | 2 | local | yes (any LLM) | Apache-2.0 | active | 4 | strict-local autonomous agent | younger than Claude Code |
| OpenHands | 2 | self-host | yes | MIT | mature | 4 | research-grade autonomous SWE agent | needs container infra |
| Cursor | 2, 5 | SaaS+local | partial | proprietary | mature | 4 | GUI fallback for non-CLI users | not fully offline |
| Windsurf | 2 | SaaS+local | partial | proprietary | mature | 3 | Cursor alt | proprietary |
| GitHub Copilot Workspace / agent mode | 2 | SaaS | no | proprietary | mature | 3 | low-friction GitHub-native | locks you to GitHub |
| OpenAI Codex (cloud, 2025+) | 2 | SaaS | no | proprietary | mature | 3 | top SWE-bench scores | cloud-only |
| SWE-agent / mini-SWE-agent | 2 | self-host | yes | MIT | mature | 3 | benchmarking + reference | not for daily work |
| Devin (Cognition) | 2 | SaaS | no | proprietary | mature | 1 | marketing reference | underperforms cheaper alternatives unassisted |
| Zed Assistant | 2 | local + LLM | yes | GPL | active | 3 | collaborative pair-programming | younger ecosystem |
| CodeRabbit | 2 | SaaS / self-host (≥500 seats) | n/a | proprietary | mature | 5 | default PR reviewer | diff-only review |
| Greptile | 2 | SaaS / self-host AWS | yes (BYO LLM) | proprietary | mature | 4 | sensitive-repo PR review | noisier than CodeRabbit |
| Sourcery | 2 | SaaS | n/a | proprietary | mature | 3 | Python/notebook lint | proprietary |
| anthropic-ai/claude-code-action | 2, 3 | self-host (GitHub Actions) | partial | MIT | active | 4 | autonomous PR review you fully control | costs Anthropic tokens |
| OpenCommit | 3 | local | yes (Ollama) | MIT | mature | 5 | AI commit messages on every commit | needs Ollama running |
| Repomix | 3, 5 | local | n/a | MIT | mature | 5 | feed any repo to any LLM | output can exceed context |
| uv | 3 | local | n/a | MIT/Apache | mature | 5 | new Python project default | newer than pip |
| pixi | 3 | local | n/a | BSD-3 | mature | 5 | bioinformatics package mgmt | conda-derived |
| Quarto | 3, 5 | local | n/a | MIT | mature | 5 | mixed-language docs and slides | learning curve |
| pre-commit + ruff + nbqa | 3 | local | n/a | MIT | mature | 5 | non-negotiable hygiene | none |
| DVC | 3 | local + cloud | n/a | Apache-2.0 | mature | 4 | data ≥1 GB | git-aware tooling friction |
| MLflow | 3 | local | n/a | Apache-2.0 | mature | 4 | default experiment tracker | UI is dated |
| Aim | 3 | local | n/a | Apache-2.0 | active | 4 | privacy-first tracker | smaller community |
| Weights & Biases | 3 | SaaS | n/a | proprietary | mature | 3 | flagship ML tracker | grant-budget hit |
| HF ml-intern | 3 | self-host | yes | Apache-2.0 | new (Apr 2026) | 3 | bookkeeping-savvy research-coding agent | numbers self-reported |
| matsengrp/plugins, VoltAgent subagents, K-Dense skills | 3 | local | yes | MIT | active | 4 | starting templates for SKILL.md | not security-audited |
| CLAUDE.md / AGENTS.md / SKILL.md spec | 3 | n/a | n/a | open spec | mature | 5 | the lab's enforceable constitution | "rules" are probabilistic |
| aicommits | 3 | local | partial | MIT | mature | 3 | leaner OpenCommit alt | OpenAI-leaning |
| cookiecutter / copier | 3 | local | n/a | BSD/MIT | mature | 4 | repo templating | none |
| Whisper Large v3 / v3-turbo | 4 | local | n/a (ASR) | MIT | mature | 5 | default ASR | turbo loses ~1 % on long-form |
| faster-whisper | 4 | local | n/a | MIT | mature | 5 | default Whisper runtime | needs CUDA libs aligned |
| WhisperX | 4 | local | n/a | BSD-4 | mature | 5 | word-alignment + diarization wrapper | installs heavy deps |
| pyannote-audio 3.1 / community-1 | 4 | local | n/a | MIT (model gated) | mature | 5 | default diarizer | HF gating breaks unattended deploys |
| Parakeet-TDT 0.6B v3 | 4 | local | n/a | CC-BY-4.0 | mature | 4 | NVIDIA-GPU European-language meetings | English-only v2 still better on English |
| NVIDIA NeMo Sortformer v2 | 4 | local | n/a | Apache-2.0 | mature | 4 | streaming diarization | degrades at 5+ speakers |
| Speaches | 4 | self-host (Docker) | yes | MIT | active | 5 | OpenAI-compatible STT/TTS backend | none |
| Meetily | 4 | self-host (desktop) | yes (Ollama) | MIT | active | 4 | full meeting-assistant on Win/macOS | Linux build-from-source |
| Whishper | 4 | self-host (Docker) | n/a | MIT | active | 4 | shared transcription web UI | no summarization |
| Obsidian whisper plugin / AI Meeting Notes | 4 | local | yes | MIT | active | 4 | "meeting notes into my vault" | OS-specific system audio |
| Speakr | 4 | self-host (Docker) | yes | MIT | active | 3 | transcription + Obsidian export | newer, smaller community |
| Otter / Fireflies / Granola / tl;dv | 4 | SaaS | no | proprietary | mature | 1 | convenience for non-sensitive talks | data leaves premises |
| Speechmatics | 4 | SaaS | no | proprietary | mature | 2 | high-end accuracy | expensive |
| Marimo | 5, 2 | local + WASM | yes (marimo pair) | Apache-2.0 | mature | 5 | reactive notebooks for journal club | WASM 2 GB cap |
| Quarto-Pyodide / quarto-live | 5 | local + static | n/a | MIT | mature | 5 | mixed-language interactive papers | Pyodide package limits |
| Pluto.jl | 5 | local + WASM | n/a | MIT | mature | 5 | Julia journal clubs | Julia-only |
| Observable Framework | 5 | local + static | n/a | ISC | mature | 4 | dataviz-driven journal clubs | JS-first |
| Hugging Face Spaces | 5, 1 | SaaS | partial | proprietary host | mature | 4 | one-click paper demos | vendor host |
| Gradio / Streamlit | 5 | local | n/a | Apache-2.0 | mature | 4 | demo SDKs | Streamlit reruns are quirky |
| Replicate / Modal | 5 | SaaS | n/a | proprietary | mature | 3 | GPU-heavy demos | cost |
| Jupyter + JupyterLite + Binder | 5 | local + WASM + cloud | n/a | BSD-3 | mature | 3 | legacy bridge | Marimo/Quarto are better defaults |
| Paper2Code / PaperCoder | 5 | self-host | yes | open | preview | 2 | scaffolding for code-less papers | non-peer-reviewed; trust low |

---

## "If You Do Nothing Else from This Report, Do These Three Things"

**1. Stand up a private PaperQA2 instance over your lab's Zotero corpus this month.** Effort: ~3 person-days for a research engineer. Prerequisite: one workstation with a 24 GB GPU (a 4090 is enough) running Ollama and a 30-billion-parameter coder/instruct model such as **GLM-4.7-Air** or **Qwen3-30B-A3B-Instruct**, plus **Docling** for PDF ingestion and **Qwen3-Embedding-0.6B** for the vector index. Off-ramp: if it does not displace ad-hoc Google searches within six weeks, rip it out — the PDFs and lockfiles are portable. This is the single highest-leverage move in this report because it delivers grounded literature search to every PI and trainee with no data leaving the lab, and it directly attacks the highest-volume daily activity scientists actually do.

**2. Commit `CLAUDE.md` + `AGENTS.md` + `pre-commit` + `uv` (and `pixi` if you have compiled tools) into every active lab repo and run **OpenCommit + Ollama** as a `prepare-commit-msg` hook.** Effort: ~1 person-day per repo for a fresh project, ~2 days for a retrofit; an afternoon for the OpenCommit hook. Prerequisite: a senior engineer who has read Patrick Mineault's ["Claude Code for Scientists"](https://www.neuroai.science/p/claude-code-for-scientists) and Anthropic's ["Long-running Claude for scientific computing"](https://www.anthropic.com/research/long-running-Claude). Off-ramp: every component is removable in `git revert`. This turns the lab's ad-hoc "we use AI a bit" into an enforceable constitution and is the prerequisite for trusting any of the more autonomous agents in Prompt B's later rungs of the adoption ladder. If you skip this step you will spend the second half of 2026 firefighting agentic-coding accidents instead of compounding.

**3. Run a four-week journal-club pilot using Marimo + WASM export + Claude Code prep, fully on-prem.** Effort: ~6 hours of presenter time across four weeks (1.5 hours/week, replacing ~2 hours of slide-making). Prerequisite: one presenter willing to learn Marimo and one engineer to set up the GitHub Pages publish step. Off-ramp: revert to slides at any point — Marimo notebooks are pure Python and translate to Jupyter or PDF in one command. This delivers the cultural shift that the rest of the daily-work tier depends on: it normalizes "the agent helps me prepare, the audience explores live, the transcript and notebook are saved together." Combined with the Whisper-based meeting capture from Part 4, the lab now produces durable, searchable institutional memory for every paper it discusses — at zero per-meeting marginal cost. Three things, three different time horizons, three different audiences in the lab. Anything else from this report can wait.