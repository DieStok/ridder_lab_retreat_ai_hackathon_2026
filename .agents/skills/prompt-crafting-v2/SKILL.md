---
name: prompt-crafting-v2
description: Craft, expand, and improve prompts for any LLM (Claude or ChatGPT / GPT-5.x / Codex) using Anthropic's and OpenAI's official best practices. Triggers when the user says "craft me a prompt", "give me a better prompt", "expand this initial query", "improve this prompt", "write a prompt for", "optimize this prompt", "make this prompt better", "help me prompt", "rewrite this prompt", "write a system prompt", "design a deep research prompt", or any request to create, refine, restructure, or enhance a prompt or system prompt for Claude, ChatGPT, GPT-5.4, GPT-5.5, GPT-5.3-codex, Codex, or any other LLM. Also triggers when the user shares a rough idea and wants it turned into a proper prompt, asks to split a long prompt, or asks for prompt engineering help of any kind.
---

# Prompt Crafting v2

Transform rough ideas or weak prompts into high-quality, structured prompts that follow the official prompt-engineering guidance for the target model.

This skill covers prompts for **both Anthropic's Claude family AND OpenAI's GPT-5.x / Codex family**. It pulls from two cached reference files in `references/`:

- `references/Claude_prompting_best_practices_04_05_2026.md` — Anthropic's official guidance for Claude Opus 4.7, Opus 4.6, Sonnet 4.6, Haiku 4.5
- `references/ChatGPT_Codex_prompting_best_practices_04_05_2026.md` — OpenAI's official guidance for GPT-5.5, GPT-5.4, GPT-5.3-codex, plus general OpenAI prompt engineering

These cached references are kept current via `scripts/regenerate_references.py` (see `scripts/USAGE.md`).

## Workflow

1. **Identify the target model** (see "Step 1: Route by target model" below). This determines which reference file to consult.
2. **Understand the goal** — what the user wants the prompt to achieve, the surface (chat / API system prompt / agentic harness / Deep Research session), and any constraints.
3. **Apply the techniques below** plus the model-specific guidance from the matching reference file.
4. **Present the result** with a brief explanation of the key choices and a pointer to the reference section(s) used.

## Step 1: Route by target model

Pick the right reference file before drafting the prompt. The two model families have meaningfully different optimal prompt styles, and applying the wrong style can hurt performance.

| Stated target model / surface | Use these references | Notes |
|---|---|---|
| Claude (Opus / Sonnet / Haiku, any 4.x) | `references/Claude_prompting_best_practices_04_05_2026.md` (line index below) + the techniques in this SKILL.md | Default if the user mentions "Claude" or pastes a Claude system prompt. |
| Claude Code, claude.ai, Anthropic API | Same as above | All Anthropic surfaces use Claude prompting conventions. |
| ChatGPT (any), GPT-5.5, GPT-5.4, GPT-5.4-mini/-nano, GPT-5.x | `references/ChatGPT_Codex_prompting_best_practices_04_05_2026.md` §§1–3 + §5 | Use §2 for GPT-5.5, §3 for GPT-5.4 and its mini/nano variants. §1 + §5 are foundational. |
| Codex CLI, Codex IDE/web, gpt-5.3-codex API | `references/ChatGPT_Codex_prompting_best_practices_04_05_2026.md` §4 (+ §1 foundationally) | Critically: §4 specifically advises *removing* the upfront-plan / preamble prompting that helps GPT-5-series models. Codex rollouts can stop early if you keep them. |
| Unknown / "any LLM" / model-agnostic | This SKILL.md alone (techniques are largely portable). Mention to the user that more specific guidance is available if they specify the target. | Stick to model-agnostic core techniques; flag to the user that you can sharpen the prompt if they name a target model. |

**Routing tips:**

- If the user pastes an existing prompt that's clearly written for one model (e.g., uses `<thinking>` tags or refers to `claude-opus-4-7`), default to that family.
- If the user says "ChatGPT" or "GPT" without a version, default to the latest mainline guide (§2 GPT-5.5).
- If the user mentions "agentic coding" or "code agent", check whether they mean Claude Code or Codex — they have different optimal prompt styles.
- When in doubt, ask once: "Is this prompt for Claude or for ChatGPT / GPT-5.x / Codex?"

**Cross-family lessons that always apply** (regardless of target):

- Be specific about output format, length, tone, and constraints.
- Use XML or markdown structure to separate instructions, context, examples, and inputs.
- Few-shot examples (3–5, diverse, representative) dramatically improve consistency.
- For long-context inputs, place documents at the top and the query at the bottom.
- Match prompt style to desired output style.

## Step 2: Read the matching reference

Both reference files are organized into addressable sections. Use these line indices to jump to the right place.

### `references/Claude_prompting_best_practices_04_05_2026.md` line index

| Topic | Lines | What you'll find |
|---|---|---|
| **Prompting Claude Opus 4.7** (latest model) | 29–184 | Verbosity & effort calibration, tool-use triggering, literal instruction following, design defaults, code review harness, computer use |
| **General principles** (clarity, context, examples, XML, roles, long context) | 186–350 | Golden rule, before/after examples, few-shot tips, XML tag best practices, multi-document structure, quote-grounding |
| **Output & formatting** (verbosity, format control, LaTeX, prefill migration) | 352–463 | Verbosity steering, markdown-minimizing prompt, LaTeX override, prefill→Structured-Outputs migration |
| **Tool use** (action bias, parallel calls) | 465–528 | Proactive-action prompt, conservative-action prompt, parallel tool-call prompt |
| **Thinking and reasoning** (overthinking, adaptive thinking, CoT, self-check) | 530–604 | Effort-based reasoning, adaptive thinking config, manual CoT fallback, self-check pattern |
| **Agentic systems** (long-horizon, state, autonomy/safety, research, subagents) | 606–785 | Context-window awareness, multi-window workflows, state tracking, autonomy guardrails, research patterns, subagent orchestration, anti-overengineering, hallucination minimization |
| **Capability-specific tips** (vision, frontend) | 787–825 | Crop-tool technique, frontend aesthetics prompt to avoid "AI slop" |
| **Migration considerations** (4.5 → 4.6, 4.6 → 4.7) | 827–end | Effort settings, adaptive-thinking migration, Sonnet 4.5 → 4.6 guide |

### `references/ChatGPT_Codex_prompting_best_practices_04_05_2026.md` line index

| Topic | Lines | What you'll find |
|---|---|---|
| **Routing preamble** (which section to use when) | 1–47 | Read this first to confirm routing for the target model |
| **§1 General prompt engineering** | 49–469 | Message roles (developer/user/assistant), reusable prompts, Markdown+XML formatting, few-shot learning, context-window planning, GPT-5 best practices for coding/frontend/agentic, reasoning vs. GPT-model differences |
| **§2 GPT-5.5 prompting guide** | 471–738 | Outcome-first prompts (less process-heavy than 5.4), preamble for time-to-first-token, stopping conditions, retrieval budgets, citations & grounding, creative drafting guardrails, phase parameter, suggested prompt structure |
| **§3 GPT-5.4 prompting guide** (incl. mini & nano) | 740–1340 | `<output_contract>`, `<tool_persistence_rules>`, `<completeness_contract>`, `<verification_loop>`, `<research_mode>`, `<citation_rules>`, coding-task patterns, personality+writing controls, reasoning-effort tuning, small-model guidance |
| **§4 GPT-5.3 Codex prompting guide** | 1342–1853 | Recommended starter prompt (Codex-Max baseline), apply_patch tool (Responses + freeform/CFG), shell_command, update_plan, view_image tool schemas, AGENTS.md mechanics, compaction, custom tool advice |
| **§5 Using GPT-5.5 (supplementary)** | 1855–end | API-level migration guidance: prompt-caching, structured outputs, Responses API, dropping the date, treating GPT-5.5 as a new family rather than a drop-in |

## Core Techniques

### Clarity and specificity

- Be explicit about desired output format, length, tone, and constraints
- Write instructions as sequential numbered steps when order matters
- Frame positively: say what to do, not what to avoid ("Write in flowing prose" > "Don't use bullet points")
- If you want above-and-beyond behavior, say so explicitly: "Include as many relevant features as possible. Go beyond the basics."

### Context and motivation

Explain *why* behind instructions — both Claude and GPT-5.x generalize from rationale better than from bare rules.

**Weak:** `NEVER use ellipses`
**Strong:** `Your response will be read aloud by a text-to-speech engine, so never use ellipses since it won't know how to pronounce them.`

### Role setting

A single sentence in the system prompt focuses behavior and tone:
`You are a senior backend engineer specializing in distributed systems and Go.`

For OpenAI: this typically goes in the `developer` role message or the `instructions` parameter; see §1 of the OpenAI reference.

### XML structure

Use XML tags to separate instructions, context, examples, and inputs — especially in complex prompts. Both Claude and GPT-5.x respond well to this pattern.

```xml
<instructions>...</instructions>
<context>...</context>
<examples>...</examples>
<input>{{USER_INPUT}}</input>
```

Use consistent, descriptive tag names. Nest when natural (`<documents><document index="1">...`).

GPT-5.4 in particular has a heavy library of named XML blocks (`<output_contract>`, `<tool_persistence_rules>`, `<verification_loop>`, etc.) — see §3 of the OpenAI reference.

### Few-shot examples

3–5 diverse examples dramatically improve accuracy and consistency. Wrap in `<examples><example>` tags. Make them relevant, diverse (cover edge cases), and representative of real use.

### Long-context prompts

For prompts with large documents (20k+ tokens):
- Place longform data at the top, query/instructions at the bottom
- Wrap documents in `<document>` tags with `<source>` metadata
- Ask the model to quote relevant passages before reasoning

### Thinking and reasoning

- For complex tasks, encourage reflection: "Think through this step by step before answering."
- Use `<thinking>` and `<answer>` tags to separate reasoning from output (Claude). For GPT-5.x reasoning models, the equivalent is the internal reasoning trace controlled by `reasoning.effort`.
- Ask the model to self-check: "Before you finish, verify your answer against [criteria]."
- Prefer general instructions ("think thoroughly") over prescriptive step-by-step plans
- For Claude 4.6/4.7, prefer adaptive thinking + the `effort` parameter over manual CoT scaffolding
- For GPT-5.5, treat reasoning effort as a *last-mile knob* — fix the prompt first; see §3 "Treat reasoning effort as a last-mile knob" of the OpenAI reference

### Output formatting control

- Tell the model what format to use, not what to avoid
- Use XML format indicators: "Write your analysis in `<analysis>` tags"
- Match prompt style to desired output style (markdown-free prompt → less markdown output)
- For minimal markdown: instruct to write in "clear, flowing prose using complete paragraphs"
- For OpenAI: also use the `text.verbosity` API parameter as an additional control layer

## Agentic & Tool-Use Prompts

### Action bias

- Be explicit about whether the model should act or suggest: "Make these edits" > "Can you suggest changes?"
- For proactive agents: "Default to implementing changes rather than only suggesting them."
- For conservative agents: "Do not make changes unless explicitly instructed."

### Parallel tool calling

If relevant, add: "If you intend to call multiple tools and there are no dependencies between the calls, make all independent calls in parallel."

For GPT-5.4 in particular, parallel + sequential rules can be made explicit via `<parallel_tool_calling>` (see §3 of the OpenAI reference).

### Safety guardrails for agents

For autonomous agents, add reversibility guidance:
- "Take local, reversible actions freely. For destructive or shared-system actions, ask first."
- List examples: deleting files, force-pushing, posting externally.

### Reducing overengineering

If the prompt is for coding tasks, consider adding: "Only make changes that are directly requested. Keep solutions simple and focused. Don't add features, refactor code, or create abstractions beyond what was asked."

### Minimizing hallucinations

For code-related prompts: "Never speculate about code you have not opened. Read relevant files BEFORE answering questions about the codebase."

For research/grounding-sensitive prompts (especially GPT-5.4/5.5): use `<citation_rules>` and `<grounding_rules>` blocks — see §3 "Lock research and citations to retrieved evidence" in the OpenAI reference.

## Codex-specific gotcha (gpt-5.3-codex)

If the target is **gpt-5.3-codex** (Codex CLI, Codex IDE, Codex API), the OpenAI guidance is opinionated about *removing* prompt patterns that work well for GPT-5-series models:

- **Remove** prompting that asks the model to communicate an upfront plan, preambles, or status updates during the rollout. These cause Codex rollouts to stop early.
- **Keep** autonomy/persistence prompting, codebase-exploration rules, tool-use rules (especially `apply_patch`), and frontend-quality rules.
- **Use** the recommended Codex starter prompt as a base (§4 of the OpenAI reference, lines 1377–1495) and add tactical pieces from there.

When converting a Claude Code prompt to Codex (or vice versa), treat this as a real port — the autonomy contracts differ.

## Anti-Patterns to Avoid

- **Vague instructions**: "Make it good" → specify what "good" means
- **Negative-only rules**: "Don't use jargon" → "Write for a general audience with no assumed technical background"
- **Over-prompting tool use**: Claude 4.6/4.7 models are proactive — avoid "CRITICAL: You MUST use this tool" language; use natural phrasing instead. Same applies to GPT-5.4/5.5.
- **Carrying over GPT-5.4 process-heavy stacks into a GPT-5.5 prompt**: GPT-5.5 wants shorter, outcome-first prompts. See §2 of the OpenAI reference.
- **Carrying over GPT-5-series upfront-plan prompting into a Codex prompt**: see "Codex-specific gotcha" above.
- **Missing examples**: If output format matters, always include examples
- **Walls of text**: Use XML tags and structure to break up complex prompts

## Prompt Template (model-agnostic starting point)

When producing a crafted prompt, use this structure as a starting point and adapt as needed:

```
[Role / system prompt — 1-2 sentences]

<instructions>
[Clear, numbered steps or directives]
</instructions>

<context>
[Background info, constraints, domain knowledge]
</context>

<examples>
<example>
<input>...</input>
<output>...</output>
</example>
</examples>

<input>
{{VARIABLE}}
</input>
```

Omit sections that aren't needed. Simpler prompts don't need all sections.

For GPT-5.5 specifically, also see the "Suggested prompt structure" template in §2 of the OpenAI reference (lines ~711–738), which uses sections like `# Goal`, `# Success criteria`, `# Stop rules`.

## Crafting Deep Research Prompts

Deep research prompts are long, highly structured prompts designed for Claude's Deep Research mode, OpenAI's Deep Research mode, or extended agentic research sessions. They produce exhaustive, literature-grounded reports and actionable research plans. These prompts are fundamentally different from chat prompts — they are closer to a research brief or grant proposal in specificity.

### Anatomy of a Deep Research Prompt

Every deep research prompt should contain these sections in order:

**1. Preamble & Role** — Assign a specific senior expert role with 3–5 numbered expertise areas directly relevant to the research question. Then provide a dense context dump of all prior work, existing systems, papers, and codebases the agent should know about. For each item, include author, year, venue, and 1–2 sentences on what it does and why it matters.

**2. Central Research Question** — State the core question in a blockquote, then decompose it into 3–7 numbered sub-questions. Each sub-question should be independently answerable but feed into the whole.

**3. Numbered Parts with Exhaustive Instructions** — Break the report into Parts (typically 3–6). Within each Part, use numbered sub-sections (1.1, 1.2...) with explicit enumeration of what to cover. For every system, tool, or technique, specify what dimensions to report on, e.g.: *"For each system, provide: (a) core algorithm, (b) matching types supported, (c) known strengths and failure modes, (d) availability and how to run it today, (e) benchmark performance."*

**4. Named Entities Everywhere** — Name specific papers (Author et al., Year), tools, GitHub repos, file paths, datasets, and URLs. Never say "review the relevant literature" — say "cover Magneto (Liu et al., VLDB 2025), LLMatch (Wang et al., 2025), and Matchmaker (Seedat & van der Schaar, NeurIPS 2024)." Include explicit search instructions: *"Search specifically for any systems published in late 2025 or 2026 that apply LLMs to schema matching."*

**5. Output Specification** — State word count target (e.g., "target 15,000+ words across all sections"), table formats, scoring frameworks, and exactly what deliverables to produce.

**6. Critical Reminders** — End with a short section reinforcing the 3–5 most important constraints, priorities, or things the agent must not forget.

### Make Every Prompt Self-Contained

A deep research prompt will be pasted into a fresh Deep Research session with no prior conversation. The agent has no access to files on the user's machine, earlier chats, or implicit project context. Therefore:

**Front-load all essential context directly into the prompt.** When the user provides background documents, papers, codebase descriptions, or prior results, extract the key information and paste it into the preamble — don't just reference it. Include: system descriptions with architecture details, key findings with numbers, named tools/libraries with versions, file paths and directory structures, dataset descriptions, and any constraints or decisions already made.

**Create an explicit context section** at the end of the prompt (before Critical Reminders) with the heading `## APPENDIX: PROJECT CONTEXT AND REFERENCE MATERIALS`. Paste verbatim or lightly condensed versions of:
- Codebase architecture descriptions or README excerpts
- Key prior results, benchmarks, or metrics the agent should know
- Relevant configuration files, schemas, or data dictionaries
- Draft introductions, contribution lists, or paper outlines
- Any information the agent would otherwise need to search for but that exists in private/unpublished materials

**The test:** Could someone with zero prior knowledge of the project paste this prompt into a fresh Deep Research session and get a useful report? If not, more context needs to be inlined.

**When crafting prompts for the user:** If the user has supplied files (papers, code, notes), read them and extract the relevant portions into the prompt's appendix. Flag what you included and why, so the user can review. This is especially important for the synthesis prompt (Prompt E), which must contain enough project context for the agent to produce a concrete plan — not just summaries of Reports A–D.

### Implementation Plans (5–6 Month Timelines)

When the prompt asks for a research plan or implementation roadmap, include these specific structures:

**Prioritization scoring framework** — Define a formula, e.g.:
`Priority Score = (Yield × Risk × Novelty) / (6 − Simplicity)` where each factor is scored 1–5 with clear definitions.

**Priority tiers** — Classify every experiment/task into tiers:
- P1 (Essential): irreducible core without which the publication cannot stand
- P2 (Important): substantially strengthens the work, feasible within the window
- P3 (Stretch): fully specified but may spill past the deadline; seeds a second publication
- P-Extra (Aspirational): requires additional infrastructure or collaborations; articulated with same specificity so they can be picked up later

**Experiment inventory table** — List ALL experiments with columns for ID, description, Simplicity, Yield, Risk, Novelty, Dependencies, and Priority tier. Instruct: *"Do not remove experiments based on feasibility — classify them instead."*

**Month-by-month timeline** with specific deliverables, go/no-go decision points, contingency plans, and dependency arrows. Include: *"What happens if Experiment X fails? What is the fallback?"*

**Codebase architecture deliverable** (when applicable) — Full directory tree, component interfaces, a diff from the current codebase, and labels showing which components are P1/P2/P3.

### Splitting into Sub-Prompts

A single deep research prompt covering multiple domains will exceed useful context and produce shallow results. Split into independent sub-prompts + a synthesis prompt when:
- The topic spans 3+ distinct technical domains
- A monolithic prompt would exceed ~750 lines of detailed instructions
- Sub-topics can be researched independently (no circular dependencies)

**The N+1 pattern**: Create N independent domain prompts (A, B, C, D...) + 1 synthesis prompt (E).

**Each sub-prompt (A–D) should:**
- Be fully self-contained with its own preamble, role, and context
- Focus on one domain (e.g., "schema matching landscape", "agent architectures", "local LLMs & methodology")
- Produce a complete standalone report
- Be runnable in parallel with the others

**The synthesis prompt (E) should:**
- Open with: *"You have been given N detailed research reports from prior deep research rounds"* and summarize what each report covers
- Re-include the full project context (codebase descriptions, key systems, draft contributions)
- Define concrete deliverables: prioritized timeline, codebase architecture, roadmap beyond the initial period
- Instruct the agent to synthesize, not repeat — cross-reference findings, resolve contradictions, identify gaps between reports

**Always include a README/execution guide** alongside the prompt files, containing:
- A table showing each prompt, its focus, estimated deep research time, and key outputs
- Execution order (which run in parallel, which depend on prior outputs)
- Instructions for feeding outputs into the synthesis prompt: *"Paste the full outputs of Prompts A–D into the conversation before or alongside Prompt E"*

### Outputting Multi-File Prompt Sets

When crafting deep research prompts for the user, **always output them as separate files**, not inline. Structure:

```
prompts_deep_research_[topic]/
├── README_prompt_execution_guide.md
├── PROMPT_A_[domain_1].md
├── PROMPT_B_[domain_2].md
├── PROMPT_C_[domain_3].md
├── PROMPT_D_[domain_4].md
└── PROMPT_E_SYNTHESIS_[plan_type].md
```

For simpler topics that don't need splitting, output a single file. For topics that are borderline, output both a monolithic version AND a split version with pieces (piece_1, piece_2...) that each correspond to one Part of the full prompt — this lets the user choose.

### Deep Research Anti-Patterns

- **"Review the literature on X"** — too vague. Name 5–15 specific systems, papers, or tools to cover, then add "search for any additional systems published in [year range]"
- **Missing search instructions** — always include explicit `**Search for:**` directives telling the agent exactly what web searches to run
- **Vague deliverables** — "provide a plan" → specify: experiment inventory table with scoring, month-by-month timeline, go/no-go decisions, contingency plans, architecture diagram
- **No priority tiers** — every plan should separate essential from aspirational work; never present a flat list
- **Monolithic prompt for multi-domain topics** — split into sub-prompts to get depth instead of breadth
- **Missing context dump** — the preamble should front-load everything the agent needs to know about existing work, codebases, prior results, and constraints. Don't make the agent guess.

## Deep Research Prompt Examples

Three real prompt sets are bundled in [examples/](examples/) as reference. When crafting deep research prompts, read the relevant example files to match the user's domain and complexity. These are production prompts that were used successfully — study their structure, not just their content.

### Example 1: Genomic sequence-to-function deep research — Monolithic + Pieces Pattern

A single-topic deep research prompt (computational genomics: sequence-to-function deep-learning models for variant-effect prediction) that exists both as one 868-line monolithic file AND as 5 separate pieces. Read this when the user needs a single focused deep research prompt, or wants to see how to split a long prompt into sequential pieces.

**Location:** [examples/genomic_sequence_to_function_models_variant_effects_deep_research/](examples/genomic_sequence_to_function_models_variant_effects_deep_research/)

| File | Lines | Patterns to study |
|---|---|---|
| `FINAL_deep_research_prompt_sequence_models_disease_SNPs.md` | 868 | **The gold standard monolithic prompt.** Study: (1) Preamble with 4 expertise areas + dense context dump of 4 systems with citations (lines 5–34); (2) Central research question in blockquote + 5 sub-questions (lines 34–44); (3) Output requirements listing 5 explicit Parts (lines 44–50); (4) Per-model enumeration with exact dimensions "(a)…(e)" (lines 38–86); (5) Explicit search directives — "Search for" appears throughout; (6) Appendix with Cancer PRS reference data pasted inline (lines 610+) |
| `piece_1_preamble_and_models.md` | 122 | How the preamble + Part 1 work as a standalone piece |
| `piece_5_synthesis_plan_and_appendix.md` | 242 | **Synthesis/plan pattern.** Study: (1) "You are now the Synthesis Agent" role shift (line 1); (2) Priority scoring formula with 5 criteria (lines 3–11); (3) Full experiment inventory table with 17 experiments, all scored (lines 17–35); (4) Month-by-month timeline structure (lines 37+); (5) Go/no-go decision points; (6) One-page executive summary request; (7) Critical reminders section at end |

### Example 2: LLM Metadata Harmonisation — N+1 Sub-Prompt Pattern

A multi-domain project (NLP + data integration + agent architectures + methodology) split into 4 parallel sub-prompts + 1 synthesis prompt. Read this when the user's topic spans multiple technical domains and needs the split pattern.

**Location:** [examples/llm_metadata_harmonisation/](examples/llm_metadata_harmonisation/)

| File | Lines | Patterns to study |
|---|---|---|
| `README_prompt_execution_guide.md` | 124 | **The execution guide template.** Study: (1) Parallel vs. sequential execution table (lines 13–30); (2) Per-prompt summaries with key outputs (lines 34–87); (3) "Key Design Decisions" section explaining *why* 4+1 instead of monolithic (lines 88–109); (4) Meta-lessons drawn from the genomic deep research example on prompt craft (lines 96–109); (5) Appendix of URLs and resources for the agent (lines 111+) |
| `PROMPT_A_schema_matching_harmonization_landscape.md` | 226 | **Domain sub-prompt pattern.** Study: (1) Self-contained preamble with its own role and full project context (lines 5–22); (2) Dense system descriptions with author/year/venue/findings pasted inline (lines 8–22); (3) Explicit "systems to cover (do not skip any)" enumeration (lines 30+); (4) "Search specifically for" directives per subsection; (5) Multi-level Part structure (3 Parts, each with numbered sub-sections) |
| `PROMPT_E_SYNTHESIS_six_month_plan_architecture.md` | 426 | **The synthesis prompt — most complex example.** Study: (1) "You have been given four detailed research reports" opening with per-report summaries (lines 5–25); (2) Full project context re-included (codebase, Matchmaker, GEO db plan, draft contributions — lines 25–45); (3) Three numbered Deliverables with precise specs (lines 45–60); (4) Priority scoring table with formula (lines 34–52); (5) Experiment inventory with ~30 rows pre-populated for the agent to score (lines 54–104); (6) Month-by-month timeline template with specific structure to follow (lines 105–210); (7) Codebase architecture deliverable with directory tree and diff instructions (lines 236–384); (8) "CRITICAL REMINDERS FOR SYNTHESIS" at end (lines 416–426) |
| `PROMPT_B/C/D` | 231–250 each | Additional domain sub-prompts — same structural pattern as A, different domains (RAG/search, agent architectures, local LLMs/methodology) |

### Example 3: Sturgeon Mechanistic Interpretability — Single Monolithic Prompt

A single deep research prompt (380 lines) for a well-scoped topic. Shorter than the genomic example but follows the same structure. Read this as an example of a mid-length prompt that doesn't need splitting.

**Location:** [examples/sturgeon_mech_int.md](examples/sturgeon_mech_int.md)

| Section | Lines | Patterns to study |
|---|---|---|
| Preamble | 5–13 | Concise role + explicit output structure and word count target ("15,000+ words") |
| Part 1: MI Techniques | 15–68 | **Exhaustive technique enumeration.** 5 major categories, each with 4–8 named techniques with author/year. The "(a)…(e)" per-technique dimension pattern |
| Part 2: Landscape | 71–101 | Timeline-of-papers pattern organized by thematic arcs, not just chronologically |
| Part 3: Model Analysis | 103–127 | Applying general techniques to a specific architecture — concrete layer numbers, parameter counts |
| Part 4: Plan of Attack | 127–278 | **4 parallel approaches (A–D)**, each with specific techniques, expected outputs, and risk assessment. Shows how to structure alternative approaches within a single prompt |
| Part 5: Hypotheses | 280–380 | Named hypotheses (H1–H3+) with explicit experimental protocols and expected outcomes |

## Refreshing the cached references

The two files in `references/` are point-in-time caches of public documentation pages. Source URLs and the fetch date are at the top of each file. When the live pages drift from these caches:

1. Run `python scripts/regenerate_references.py` from the skill root to refetch and rewrite both files.
2. Run with `--check` for CI-style verification that the local files still match the live sources.
3. See `scripts/USAGE.md` for setup, dependencies, and the structure of `scripts/sources.yaml`.

This keeps the skill's prompt-engineering guidance aligned with the latest official sources without the LLM having to fetch on every use.
