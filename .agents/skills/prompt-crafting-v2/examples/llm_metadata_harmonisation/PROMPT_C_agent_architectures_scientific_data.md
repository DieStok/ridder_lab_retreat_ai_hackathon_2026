# Deep Research Prompt C: Agent Architectures for LLM-Based Scientific Data Processing — From Coding Agents to Multi-Agent Orchestration

---

## PREAMBLE AND INSTRUCTIONS TO THE RESEARCH AGENT

You are a senior AI systems engineer with deep expertise in: (1) LLM agent architectures (ReAct, CodeAct, tool-use, coding agents), (2) multi-agent orchestration frameworks (LangGraph, CrewAI, AutoGen, OpenAI Swarm), (3) production LLM systems design (context engineering, observability, sandboxing), and (4) scientific automation and agentic AI for research. You have been given context describing:

- **Our research codebase (forked from Harmonia/BDI-Kit)**: A heavily extended fork of the published Harmonia/BDI-Kit system (Lopez et al., Patterns 2026; Santos et al., 2025), adapted for scientific experimentation on metadata harmonization. The published system provides a human-in-the-loop LLM agent with 5 domain-specific tools. Our fork adds: Apptainer-sandboxed Beaker kernel execution, two primary agent paradigms (ReAct + BDI-Kit domain tools via Archytas, and true CodeAct where the LLM writes Python in markdown fences via a custom CodeActAgentLoop), Phoenix/OTel tracing, a 20-class failure taxonomy, a Plotly Dash dashboard with 8 tabs, YAML-configured automated experiment orchestration, and support for 100+ models via litellm. This fork is the testbed for the research; the published BDI-Kit/Harmonia is a separate citable artifact.
- **SRAgent**: An agent for single-cell RNA-seq data harmonization using LangGraph with sub-agent composition (agent-as-tool factory), per-agent model configuration, structured output with retry, fan-out/fan-in for parallel tool calls, and rich console display.
- **Claude Code source code**: A frontier coding agent with bash tool, file editing (str_replace), read operations, multi-provider support, context engineering patterns, and minimal-but-effective system prompts.
- **The pi-coding-agent** (Zechner, 2025): An opinionated minimal coding agent philosophy — minimal system prompt, minimal toolset (read, write, bash, browser), YOLO by default, no plan mode, no sub-agents, no MCP, cross-provider context handoff, structured split tool results.
- **Recursive Language Models** paper: Showing that a master LLM iteratively calling sub-LLMs over parts of large context files outperforms huge monolithic prompts and scales to much longer contexts.
- **Kosmos AI scientist**: An autonomous AI scientist paper providing context for agentic applications in science and open-ended agent validation.

**Your task is to produce an exhaustive research report** that addresses:

> ***What is the optimal agent architecture for LLM-based omics metadata harmonization — comparing single-agent (flat ReAct, CodeAct) vs. multi-agent (hierarchical, fan-out) vs. frontier coding agent approaches — and how should this architecture be designed for observability, deterministic reproducibility, and scientific experimentation?***

---

## PART 1: AGENT ARCHITECTURE TAXONOMY FOR DATA PROCESSING TASKS

### 1.1 Single-Agent Architectures

**Architecture A: ReAct + Domain Tools (our research fork — bdikit_context paradigm)**
- The LLM has access to 5 domain-specific tools: match_schema, rank_schema_matches, match_values, materialize_mapping, get_gdc_acceptable_values
- Conversation managed by Archytas ReActAgent with structured JSON tool calls
- Advantages: Constrained action space, domain-specific tools abstract complexity
- Disadvantages: Single-point-of-failure, tools become a bottleneck if they fail, the LLM must manage the entire workflow in one conversation
- **Search for**: Archytas framework documentation and capabilities. How does it compare to LangChain's ReAct implementation?

**Architecture B: True CodeAct (our research fork — codeact_context paradigm)**
- LLM writes Python directly in markdown fences, CodeActAgentLoop extracts and executes
- Bypasses Archytas entirely; custom loop with litellm.acompletion()
- Advantages: Natural for coding-oriented LLMs, no tool-calling format constraints, maximum flexibility — the LLM can implement any approach including writing its own schema matching logic
- Disadvantages: Less structured, harder to parse and trace, no guardrails from domain-specific tools

**Architecture C: Frontier Coding Agent (Claude Code / Codex in full-auto)**
- Give the data files + a CLAUDE.md or skills file with GDC schema context + the task description
- Let the agent run with bash, file read/write, and search tools
- **This is the most important baseline.** Search for: "Claude Code data processing automation" and "Codex data wrangling" — has anyone used frontier coding agents for metadata harmonization?
- **Key question from pi-coding-agent philosophy**: Does a minimal toolset (read, write, bash) with a well-crafted system prompt outperform a complex tool-based agent?

**Architecture D: Compositional LM Program (Matchmaker pattern)**
- A multi-stage pipeline of distinct LLM calls — NOT an agent loop, but a fixed pipeline:
  1. Candidate generation (semantic retrieval + LLM reasoning with CoT)
  2. Candidate refinement (LLM narrows combined candidates)
  3. Confidence scoring (MCQ format with abstain option)
- No tool use, no agent loop, no iterative refinement within a single run
- Self-improvement via DSPy bootstrapping: synthetic in-context examples selected from high-scoring traces
- **Key advantages**: Deterministic pipeline structure (each run follows the same stages), compositional optimization (each stage's prompts can be independently optimized), and the striking finding that this approach with GPT-3.5 matches a simpler architecture with GPT-4 — suggesting pipeline design compensates for model weakness
- **Key disadvantages**: No adaptability within a run (if candidate generation fails, there's no recovery mechanism), fixed pipeline doesn't handle unexpected data structures, schema-only (doesn't leverage instance data)
- **Relevance**: This is a fundamentally different paradigm from agent-based approaches. The question for our project is: for GEO metadata harmonization (which involves BOTH schema matching AND value mapping), is a fixed compositional pipeline sufficient, or do we need the adaptability of an agent loop?
- **Human-in-the-loop**: Matchmaker demonstrates entropy-based deferral — using confidence score entropy to identify uncertain matches and escalate to humans. This consistently outperforms random deferral and is directly applicable to our pipeline's human-in-the-loop requirements.

**Architecture E: Direct prompting (no agent loop)**
- Single LLM call with the metadata table + GDC schema + instructions in the prompt
- No tool use, no iterative refinement
- The simplest possible approach; important as a baseline
- Expected to work for simple tables but fail on complex multi-column, many-value tasks

For each architecture: describe the agent loop (or lack thereof), what context is managed, how errors are handled, and expected strengths/weaknesses for the specific task of GEO metadata harmonization. **Pay particular attention to the spectrum from simplest (E: direct prompting) through fixed-pipeline (D: Matchmaker-style) through adaptive-agent (A/B: ReAct/CodeAct) through multi-agent (F–H) — at what complexity level does the task of GEO metadata harmonization sit?**

### 1.2 Multi-Agent Architectures

**Architecture F: Hierarchical Supervisor (SRAgent pattern)**
- A supervisor/orchestrator agent delegates to specialist sub-agents:
  - Schema Expert: Focused on column-to-GDC mapping with deep GDC knowledge
  - Value Mapper: Focused on transforming values to GDC vocabulary
  - Validator: Checks outputs against GDC constraints
  - Materializer: Produces deterministic Python code for the mapping
- Each sub-agent can have its own model, temperature, and system prompt
- Agent-as-tool-factory pattern: each sub-agent can be tested standalone or composed
- **Search for**: LangGraph multi-agent patterns 2025 2026. The supervisor pattern vs. the router pattern. How to implement agent-as-tool in LangGraph.

**Architecture G: Fan-out/Fan-in (parallel sub-agents)**
- For multi-table harmonization: fan out to N parallel agents, each harmonizing one table, then fan in to a merge agent
- Potential for significant speedup on N-table tasks
- **Search for**: LangGraph fan-out patterns. Parallel agent execution in AutoGen/CrewAI.
- Risk: consistency across parallel agents (different agents may map the same concept differently)

**Architecture H: Recursive Language Model pattern**
- Master LLM decomposes a large metadata table into sub-problems (e.g., process 5 columns at a time)
- Calls sub-LLMs with focused context for each sub-problem
- Aggregates results
- Directly addresses context window limitations for large tables
- **Search for**: The recursive language models paper (should be in the provided materials). Any follow-up work or implementations of this pattern.

**Architecture I: Critic/Verifier pattern**
- Primary agent produces a mapping; a separate critic agent evaluates it
- If the critic identifies errors, the primary agent is re-invoked with feedback
- **Search for**: Constitutional AI-style critic patterns for data quality. Debate/verification multi-agent patterns.

For each multi-agent architecture: estimate the additional complexity, implementation effort, cost multiplier (more LLM calls), and expected benefit over single-agent approaches.

### 1.3 The Agent Simplicity vs. Capability Tradeoff

The pi-coding-agent philosophy argues that simpler agents with minimal tools and well-crafted prompts outperform complex multi-agent systems. The SRAgent approach argues for rich multi-agent orchestration. **Who is right, and under what conditions?**

1. **Task complexity threshold**: At what level of task complexity do multi-agent approaches justify their overhead? A single-table harmonization may not need sub-agents; a 10-table harmonization with cross-table consistency requirements might.

2. **Model capability threshold**: Frontier models (Claude Opus, GPT-5) may handle the entire task in a single agent, while smaller local models may need task decomposition to manage complexity.

3. **The context engineering argument**: pi-coding-agent's Mario Zechner argues that controlling exactly what goes into the model's context is paramount. Complex multi-agent systems make this harder because each sub-agent's output becomes context for another. How to maintain context quality in multi-agent pipelines?

4. **Empirical evidence**: **Search for**: Papers that compare single-agent vs. multi-agent performance on data processing tasks. The "Why do multi-agent LLM systems fail?" paper (Cemri et al., 2025). "AI agents that matter" (Kapoor et al., 2024) — what does it say about when agents add value?

---

## PART 2: OBSERVABILITY, TRACING, AND DETERMINISTIC REPRODUCIBILITY

### 2.1 Observability Requirements

For scientific experimentation with agent architectures, observability is non-negotiable:

1. **What must be traced**: Every LLM call (prompt, completion, token counts, cost, latency), every tool invocation (input, output, duration), every agent decision point, every error/retry
2. **Span hierarchy**: How should traces be structured for single vs. multi-agent architectures?
3. **Current implementation in our research fork**: Phoenix/OTel with span hierarchy (AGENT → CHAIN → LLM → TOOL). How to extend this for multi-agent architectures?

**Search for**: 
- "LLM observability platform comparison 2025 2026" (Phoenix, LangSmith, Langfuse, Weights & Biases Weave, OpenLLMetry)
- "multi-agent tracing observability" — how do existing platforms handle multi-agent traces?
- "OpenTelemetry LLM agent tracing" — the emerging standard

### 2.2 Deterministic Reproducibility

A core requirement: given the same input data and configuration, the pipeline should produce a deterministic mapping that can be re-executed without LLM calls.

1. **The materialize_mapping pattern**: BDI-Kit produces a Python script that applies the discovered mapping deterministically. This separates the LLM-assisted discovery phase from the deterministic execution phase.

2. **Configuration snapshots**: Our research fork saves config_snapshot.yaml with each run. How to make this sufficient for full reproducibility (including model version, temperature, system prompt hash)?

3. **Caching LLM calls**: If the same prompt is sent twice, should the system return a cached result? This enables exact reproducibility but prevents the LLM from potentially finding a better answer on retry.

4. **Versioning of prompts, tools, and schemas**: How to track changes to system prompts, tool descriptions, and target schemas across experiments?

**Search for**: "LLM experiment reproducibility" and "deterministic LLM pipeline" — best practices for reproducible AI experiments.

### 2.3 The Human-in-the-Loop Interface

The draft introduction emphasizes human-in-the-loop operation. What UI patterns work best?

1. **AskUserQuestion pattern**: Sub-agents surface concerns to the user (e.g., "Column 'Stage' could map to either 'ajcc_pathologic_stage' or 'clinical_stage' in GDC. Which is correct?"). How to implement this cleanly?
2. **Progressive disclosure**: Show the user a summary of what the agent did, with drill-down capability to inspect individual mapping decisions.
3. **Comparison view**: Side-by-side comparison of mappings from different agent runs / models / configurations.
4. **Approval workflow**: The user can approve, reject, or modify individual mapping decisions before the final output is produced.

**Search for**: "human-in-the-loop LLM agent UI patterns" and "interactive data integration UI"

---

## PART 3: SANDBOXED EXECUTION ENVIRONMENTS

### 3.1 Current Setup: Beaker in Apptainer

The current system runs the LLM agent inside an Apptainer container with a Beaker kernel. This provides:
- Filesystem isolation (read-only data mount, writable results mount)
- Python environment control (.venv with specific packages)
- GPU passthrough for local models (Ollama)

Limitations:
- Beaker/Archytas has a single-model assumption
- No native support for multi-agent orchestration
- Container rebuild required for dependency changes

### 3.2 Alternative Sandboxing Approaches

**Search for and compare**:
1. **E2B (e2b.dev)**: Cloud-based sandboxed execution for AI agents. How does it compare to Apptainer for scientific use?
2. **Daytona**: Development environment management for AI agents. Relevant for reproducible experiment setup.
3. **Modal**: Serverless GPU infrastructure. Could be used for running experiments in parallel.
4. **Docker + gVisor**: More standard containerization with security sandboxing.
5. **Firecracker microVMs**: Lightweight VMs for agent execution. Used by some coding agent platforms.

For the specific use case (HPC cluster, SLURM, local GPUs, scientific experiments): which sandboxing approach is best? What are the tradeoffs?

### 3.3 Running Coding Agents in Sandboxed Environments

For the "frontier coding agent as baseline" experiment (Architecture C), we need to run Claude Code or similar in a sandboxed environment with:
- Access to the input data files (read-only)
- Access to the GDC schema (read-only)
- Python environment with relevant packages (pandas, numpy, etc.)
- Network access for API calls (if using cloud models)
- Output directory for results

**Search for**: "Claude Code headless automation" and "Claude Code batch processing" — can Claude Code be run in automated mode inside containers? What about Codex CLI?

---

## PART 4: SPECIFIC ARCHITECTURAL RECOMMENDATIONS

### 4.1 What Should Change in the Current Research Fork Architecture

Based on the analysis above, provide specific recommendations:

1. **Keep or replace Beaker/Archytas?** What does Beaker provide that cannot be achieved with a simpler approach (e.g., direct litellm calls + subprocess for code execution)?
2. **Add multi-agent orchestration?** If so, which framework (LangGraph, custom, none)?
3. **Add per-agent model configuration?** (Per the SRAgent pattern)
4. **Add structured output validation?** (Per the SRAgent pattern)
5. **Add streaming progress display?** (Per the SRAgent Rich console pattern)
6. **Keep or replace the Apptainer sandbox?**

### 4.2 Proposed Architecture for the Final System

Design a proposed architecture diagram (in text/Mermaid format) showing:
- The search pipeline components
- The harmonization pipeline components
- The observability layer
- The human-in-the-loop interface
- The experiment management layer
- How data flows between components

### 4.3 Implementation Priority

Which architectural changes should be made first (for the first publication) vs. later:
- **Phase 1 (months 1–2)**: Minimal changes needed to run the benchmark experiments
- **Phase 2 (months 3–4)**: Architectural improvements based on Phase 1 learnings
- **Phase 3 (months 5–6)**: Production-ready system for ongoing use

---

## SEARCH QUERIES TO EXECUTE

1. "ReAct CodeAct coding agent comparison data processing 2025 2026"
2. "LangGraph multi-agent pattern supervisor 2025 2026"
3. "Why multi-agent LLM systems fail Cemri 2025"
4. "AI agents that matter Kapoor 2024 recommendations"
5. "Claude Code headless automation batch"
6. "coding agent vs tool-use agent performance comparison"
7. "LLM observability Phoenix LangSmith Langfuse comparison 2025 2026"
8. "deterministic LLM pipeline reproducibility"
9. "human-in-the-loop LLM agent interactive UI"
10. "context engineering LLM agent 2025 best practices"
11. "E2B sandbox agent execution"
12. "recursive language model sub-LLM decomposition"
13. "pi-coding-agent minimal agent architecture"
14. "SRAgent single cell RNA-seq harmonization"
15. "Kosmos AI scientist autonomous agent validation"
16. "OpenTelemetry LLM agent tracing multi-agent"

---

## CRITICAL REMINDERS

- **The key empirical question is: does a bespoke agent pipeline outperform giving a frontier coding agent (Claude Code / Codex) the data and letting it figure it out?** This must be tested head-to-head.
- **Simplicity is a feature.** The pi-coding-agent philosophy of minimal toolset + well-crafted prompt should be taken seriously. Multi-agent complexity must justify its overhead.
- **Observability is not optional.** Every architecture must support full tracing for scientific comparison.
- **The environment is HPC with SLURM and Apptainer.** Cloud-only solutions should be noted as alternatives but the primary architecture must work on-premises.
- **Context engineering matters more than architecture.** What's in the prompt and how context is managed across turns may matter more than ReAct vs. CodeAct vs. multi-agent. Always connect architectural choices to context quality.
