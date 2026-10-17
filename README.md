# RepoLens: AST-Grounded Agentic Self-Correction for Hallucination Reduction in Repository Architecture Synthesis

**RepoLens** is an advanced agentic software engineering framework designed to automate the generation of truthful repository documentation (`README.md`) and verified visual architecture diagrams (`Mermaid.js`). By combining multi-agent role distribution with a strict compiler-level Abstract Syntax Tree (AST) verification loop, RepoLens eliminates ghost function signatures, misattributed parameters, and broken API routes commonly produced by standard text RAG systems.

---

## Project Overview

- **Project Code:** G1-RepoLens
- **Group Head:** Zaryab Ahmad Ayaz Durrani (22i-1212)
- **Section:** CS-B / Agentic-AI
- **Course:** AI4015 — Agentic Artificial Intelligence (Fall 2026)
- **Institution:** National University of Computer and Emerging Sciences (FAST-NUCES), Islamabad Campus
- **Base Methodology:** Extended from *CodeR: An Agentic Framework for Repository-Level Code Generation and Understanding* (ICSE 2025).

---

## Core Architecture & Execution Flow

RepoLens operates via a closed-loop multi-agent orchestration pipeline:

1. **Ingestion & AST Symbol Extraction:** Clones the target GitHub repository and uses language-specific AST engines (`ast` module for Python, TypeScript Compiler API) to extract structured JSON symbol tables containing function signatures, class hierarchies, and import dependencies.
2. **Multi-Agent Generation:** 
   - **Scanner Agent:** Traverses file trees and maps module boundaries.
   - **Synthesizer Agent:** Drafts comprehensive Markdown guides and drafts initial Mermaid.js architecture flowcharts using open-weight models (DeepSeek-R1 / Qwen2.5-Coder-32B).
3. **AST-Grounded Verification Loop (Core Innovation):** A deterministic **Verifier Agent** cross-checks every generated function signature, argument list, and API route directly against the raw AST symbol table. If discrepancies or hallucinations are detected, an automated corrective feedback loop is triggered to rewrite the faulty section.
4. **Final Deliverable Synthesis:** Outputs a verified `README.md`, an `architecture.mmd` graph, and a verification audit report.

---

## Repository Structure

RepoLens/
├── src/
│   ├── ingestion/       # AST symbol table extraction and repository cloning
│   ├── agents/          # Multi-agent role implementations (Scanner, Synthesizer, Verifier)
│   └── verification/    # Deterministic AST cross-validation engine
├── benchmarks/          # Evaluation suites across Small, Medium, and Large repos
├── docs/                # Generated documentation artifacts and architecture graphs
├── requirements.txt     # Python environment dependencies
└── README.md            # Repository overview

---

## Primary Metrics & Target Goals

- **Hallucination Rate (HR):** Target < 5% error rate on generated function signatures and routes.
- **Graph Edit Distance (GED):** Minimize structural node/edge edit distance relative to expert ground-truth architecture topologies.
- **Visual Clarity:** Blind expert evaluation target of >= 4.0 / 5.0 Likert score.

---

## Quickstart & Installation

### Prerequisites
- Python 3.10+
- Git
- Local LLM inference engine (Ollama or vLLM running DeepSeek-R1 / Qwen2.5-Coder)

### Setup

git clone https://github.com/Zaryab-aakd/RepoLens.git
cd RepoLens

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

---

## License
This project is developed as part of the academic coursework for AI4015 Agentic AI at FAST-NUCES Islamabad Campus. Open-source release under the MIT License.
