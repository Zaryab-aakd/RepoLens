# RepoLens Architecture Specification

## 1. System Overview

RepoLens is an agentic framework designed to automate repository comprehension, truthful documentation synthesis, and architectural diagram extraction.

```
       +-------------------------------------------------------------+
       |                  Target Repository Source                   |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                     ScannerAgent                            |
       |  - Python AST Parser (classes, functions, routes, imports)  |
       |  - JS/TS Lexical Parser (modules, exports, routes)          |
       |  - DependencyGraphBuilder (NetworkX directed topology)      |
       +-------------------------------------------------------------+
                                      |
                         [AST Symbol Table & Matrix]
                                      |
                                      v
       +-------------------------------------------------------------+
       |                    SynthesizerAgent                         |
       |  - Generates Markdown Documentation Guide                   |
       |  - Synthesizes Programmatic Mermaid.js Flowchart            |
       +-------------------------------------------------------------+
                                      |
                             [Draft Synthesis]
                                      |
                                      v
+----->+-------------------------------------------------------------+
|      |                     VerifierAgent                           |
|      |  - Regex Claim Extraction (signatures, routes, nodes)       |
|      |  - Deterministic Compiler AST Symbol Cross-Validation       |
|      |  - Computes Hallucination Rate (HR) and Precision           |
|      +-------------------------------------------------------------+
|                                     |
|               +---------------------+---------------------+
|               |                                           |
|       [Discrepancies Found]                        [100% Valid]
|               |                                           |
|               v                                           v
+-- [Diagnostic Feedback Loop]                   +----------------------+
    - Pinpointed ghost functions                 |  Verified Artifacts  |
    - Mismatched parameters                      |  - README.md         |
    - Nonexistent routes                         |  - architecture.mmd  |
                                                 |  - report.json       |
                                                 +----------------------+
```

## 2. Multi-Agent Role Separation

1. **ScannerAgent (`src/agents/scanner_agent.py`)**
   - Ingests repository files without execution.
   - Extracts symbol hierarchies, functions, arguments, type hints, docstrings, classes, methods, and REST route decorators.
   - Constructs a cross-module directed graph `G = (V, E)`.
   - Directly addresses **Gap 1: Context Fragmentation & Topology Loss**.

2. **SynthesizerAgent (`src/agents/synthesizer_agent.py`)**
   - Synthesizes high-level system descriptions, architectural module indexes, and API references.
   - Converts topological graph structures into valid `flowchart TD` Mermaid diagrams with modular subgraphs.
   - Directly addresses **Gap 3: Visual Topology Mismatch**.

3. **VerifierAgent (`src/agents/verifier_agent.py`)**
   - Parses explicit claims made in the synthesized artifacts.
   - Intercepts hallucinated symbols by executing exact set membership and parameter matching against `RepositoryAST`.
   - Generates actionable diagnostics to guide the self-correction loop.
   - Directly addresses **Gap 2: Unverified Signature Hallucinations**.
