# RepoLens: AST-Grounded Agentic Self-Correction for Hallucination Reduction in Repository Architecture Synthesis

**RepoLens** is an agentic software engineering framework designed to automate the generation of truthful repository documentation (`README.md`) and verified visual architecture diagrams (`Mermaid.js`). By combining multi-agent role distribution with a strict compiler-level Abstract Syntax Tree (AST) verification loop, RepoLens eliminates ghost function signatures, misattributed parameters, and broken API routes commonly produced by standard text RAG systems.

---

## Project Overview

- **Project Code:** G1-RepoLens
- **Group Head:** Zaryab Ahmad Ayaz Durrani (22i-1212)
- **Section:** CS-B / Agentic-AI
- **Course:** AI4015 — Agentic Artificial Intelligence (Fall 2026)
- **Institution:** National University of Computer and Emerging Sciences (FAST-NUCES), Islamabad Campus
- **Base Methodology:** Extended from *CodeR: An Agentic Framework for Repository-Level Code Generation and Understanding* (ICSE 2025, CORE A*).

---

## Targeted Research Gaps

RepoLens directly addresses three key research limitations identified in current repository-level AI documentation tools:

1. **Context-Window Structural Loss:** Standard RAG truncates deep class hierarchies and dependency paths, leading to missing module relationships.
2. **Hallucination of Non-Existent Interfaces:** Text-only LLMs frequently synthesize "ghost" function signatures and outdated API routes that do not exist in the codebase.
3. **Static Diagram Disconnect:** Existing tools generate visual diagrams without cross-verifying nodes against actual AST symbol tables, resulting in architecturally inaccurate flowcharts.

---

## Core Architecture & Execution Flow

RepoLens operates via a closed-loop multi-agent orchestration pipeline running local open-weight models (DeepSeek-R1 / Qwen2.5-Coder-32B):

1. **Ingestion & AST Symbol Extraction:** Clones target repositories and uses language-specific AST engines (`ast` module for Python, TypeScript Compiler API) to extract structured JSON symbol tables containing function signatures, class hierarchies, and import dependencies.
2. **Multi-Agent Generation:** 
   - **Scanner Agent:** Traverses file trees and maps module boundaries.
   - **Synthesizer Agent:** Drafts comprehensive Markdown guides and initial Mermaid.js architecture flowcharts.
3. **AST-Grounded Verification Loop:** A deterministic **Verifier Agent** cross-checks every generated function signature, argument list, and API route directly against raw AST symbol tables. Discrepancies trigger an automated corrective feedback loop to rewrite faulty sections.
4. **Final Deliverable Synthesis:** Outputs a verified `README.md`, an `architecture.mmd` graph, and an audit report.

---

## Repository Structure

<pre>
RepoLens/
├── src/
│   ├── ingestion/       # AST symbol table extraction and repository cloning
│   ├── agents/          # Multi-agent role implementations (Scanner, Synthesizer, Verifier)
│   └── verification/    # Deterministic AST cross-validation engine
├── benchmarks/          # Evaluation suites across 10 target repositories
├── docs/                # Generated documentation artifacts and architecture graphs
├── requirements.txt     # Python environment dependencies
└── README.md            # Repository overview
</pre>

---

## Evaluation & Benchmark Design

- **Target Benchmark:** Evaluated across 10 open-source repositories spanning small, medium, and large codebases.
- **Evaluation Rigor:** Structural AST validation checks are strictly separated from ground-truth quality checks to avoid circular bias.
- **Human Evaluation:** Final visual clarity and architecture diagram fidelity are evaluated by 2 independent human reviewers using a 5-point Likert scale.
- **Primary Metrics:**
  - **Hallucination Rate ($HR$):** Target $< 5\%$ error rate on generated function signatures and routes.
  - **Graph Edit Distance ($GED$):** Structural node/edge edit distance relative to expert ground-truth architecture topologies.
  - **Visual Clarity:** Expert evaluation target of $\ge 4.0 / 5.0$.

---

## Quickstart & Installation

### Prerequisites
- Python 3.10+
- Git
- Local LLM inference engine (Ollama or vLLM running DeepSeek-R1 / Qwen2.5-Coder)

### Setup

1. Clone the repository:
   git clone https://github.com/Zaryab-aakd/RepoLens.git
   cd RepoLens

2. Create and activate virtual environment:
   python3 -m venv venv
   source venv/bin/activate

3. Install dependencies:
   pip install -r requirements.txt

---

## License

This project is developed as part of the academic coursework for AI4015 Agentic AI at FAST-NUCES Islamabad Campus. Open-source release under the MIT License.
