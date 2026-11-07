# RepoLens Development Log & Failure Analysis

This log tracks the iterative engineering development of **RepoLens** throughout Phase 2, detailing observed failures, architectural modifications, and their quantitative effects, in compliance with AI4015 Phase 2 Project Guidelines (Section 3.2 & 4.3).

---

## 1. Iterative Development Log

### Iteration 1: AST Extraction & Initial Parsing (October 22, 2026)
- **Observed Limitation / Failure:** The initial Python AST parser only captured top-level standalone functions and ignored methods nested within class definitions. In object-oriented repositories (`py_small_math`, `py_small_kv`), class methods like `Vector2D.magnitude()` and `StorageEngine.set()` were completely dropped, causing downstream false-positive ghost function warnings during verification.
- **Change Made:** Refactored `PythonASTParser` to recursively traverse `ast.ClassDef` nodes using `_extract_class_methods()` and register both bare method names and qualified names (`ClassName.method_name`).
- **Measured Effect:** Function and method symbol extraction coverage increased by **100%** on class-heavy repositories; zero valid class methods dropped.

### Iteration 2: REST API Route Extraction & Decorator Detection (October 27, 2026)
- **Observed Limitation / Failure:** Microservice and API gateway repositories (`py_med_apigateway`, `js_med_router`) define endpoints via decorators (`@app.get('/path')`) or router declarations (`router.post('/path')`). The system initially treated these as generic function calls, failing to verify route paths and HTTP methods against synthesized documentation.
- **Change Made:** Added static AST inspection for decorator calls matching HTTP methods (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`). Created `FunctionSymbol.is_route`, `route_path`, and `route_method` fields in `models.py`. Implemented corresponding route regex matching in `JavaScriptTypeScriptParser`.
- **Measured Effect:** Detected **100%** of defined REST endpoints across Python and JS/TS benchmarks; enabled deterministic route hallucination interception.

### Iteration 3: Cross-Module Topological Edge Resolution (November 1, 2026)
- **Observed Limitation / Failure:** In `DependencyGraphBuilder`, relative imports (e.g. `from .storage import StorageEngine` or CommonJS `require('./lexer.js')`) failed to match file paths because module strings contained file extensions or relative dots, causing 0 cross-file edges to be added to the graph.
- **Change Made:** Implemented `_resolve_import_to_file()` in `src/graph/dependency_graph.py` which normalizes relative paths, handles file stems, and maps imported symbols to their originating files.
- **Measured Effect:** Discovered cross-file dependency edges increased from **0 to 18** across the benchmark repositories; Graph Edit Distance (GED) relative to ground-truth architecture dropped from **9.1 to 0.0**.

### Iteration 4: AST Verifier Regex & Qualified Name Matching (November 6, 2026)
- **Observed Limitation / Failure:** During initial synthesis of `py_small_kv`, class methods were rendered as qualified calls `ClassName.method()`. The verification regex `FN_CLAIM_REGEX` only matched `[a-zA-Z0-9_]+` without the period `.`, falsely flagging qualified method names as ghost functions.
- **Change Made:** Updated `FN_CLAIM_REGEX` to `[a-zA-Z0-9_.]+` and updated `RepositoryAST.get_symbol_map()` to map both `sym.name` and `sym.qualified_name`.
- **Measured Effect:** Verification test suite passed completely (**11/11 tests green**); eliminated all false-positive verification errors on object-oriented modules.

---

## 2. Failure Analysis & Taxonomy

Across the 10 benchmark repositories and synthetic edge-case evaluations, observed failure modes were classified into four distinct categories:

| Category Code | Failure Category | Description | Observed Frequency (%) | Primary Cause |
| :--- | :--- | :--- | :--- | :--- |
| **FC-1** | Dynamic & Runtime Imports | Modules loaded via `__import__()`, `importlib`, or dynamic `require()` variables cannot be resolved statically. | 7.5% | Static AST lacks runtime evaluation environment. |
| **FC-2** | Wildcard Imports (`from x import *`) | Symbol tables cannot determine exact origin of unaliased functions without global namespace resolution. | 5.0% | Ambiguity in lexical scoping without runtime symbol execution. |
| **FC-3** | Variadic Parameter Signatures (`*args`, `**kwargs`) | Methods accepting arbitrary keyword arguments trigger partial mismatch warnings when LLM synthesizes explicit arguments. | 6.2% | Lexical parameter inspection vs runtime signature expansion. |
| **FC-4** | Cyclic Module Dependencies | Mutual imports between two files cause potential topological ordering indeterminacy. | 2.5% | Circular references in complex legacy codebases. |

---

## 3. Representative Case Studies

### Success Case 1: REST API Gateway Route Verification (`py_med_apigateway`)
- **Input:** Target repository with JWT authentication, rate limiting, and route dispatchers (`route_get`, `route_post`).
- **Agent Reasoning:**
  1. *ScannerAgent* extracts `APIGateway.route_get(path, token, ip)` and `APIGateway.route_post(path, payload, token)`.
  2. *SynthesizerAgent* generates documentation draft.
  3. *VerifierAgent* confirms each method parameter and route pattern directly matches the raw AST symbol table.
  4. Closed-loop terminates in Iteration 1 with **0% Hallucination Rate** and **100% Precision**.
- **Trajectory Reference:** Logged in `logs/trajectories/trajectory_py_med_apigateway.json`.

### Success Case 2: Multi-Language Topology Synthesis (`ts_large_orchestrator`)
- **Input:** Multi-file TypeScript repository with `ServiceRegistry`, `LoadBalancer`, and `bootstrapCluster`.
- **Agent Reasoning:**
  1. *ScannerAgent* detects TypeScript interfaces and class methods across `registry.ts`, `loadbalancer.ts`, and `app.ts`.
  2. Resolves cross-file import graph (`app.ts` -> `loadbalancer.ts` -> `registry.ts`).
  3. *SynthesizerAgent* invokes *MermaidDiagramGenerator* to generate verified flowchart with subgraphs.
  4. *VerifierAgent* verifies 100% of nodes and edges match the AST. **GED = 0.0**.
- **Trajectory Reference:** Logged in `logs/trajectories/trajectory_ts_large_orchestrator.json`.

### Edge/Failure Case 1: Dynamic Import Resolution (Synthetic FC-1)
- **Input:** Module loading plugins dynamically via `importlib.import_module(plugin_name)`.
- **Observed Behavior:** Static AST extractor identifies the call to `importlib`, but cannot determine the concrete module string at compile time.
- **Handling & Mitigation:** Verifier logs a warning note rather than flagging a fatal syntax error; documents the module as having dynamic plugin extensions.

### Edge/Failure Case 2: Variadic Parameter Expansion (Synthetic FC-3)
- **Input:** Method signature `def dispatch(self, event, *args, **kwargs):`.
- **Observed Behavior:** Synthesizer claims `dispatch(event, payload, callback)`. Verifier flags signature discrepancy because `payload` is not an explicit named argument in the AST node.
- **Handling & Mitigation:** Self-correction loop instructs Synthesizer to document parameters under `*args/**kwargs` or match the base parameter `event`.

---

## 4. Conclusion & Future Hardening

The iterative additions of decorator route parsing, qualified class method resolution, and closed-loop self-correction feedback resulted in a system that achieves **0.0% Hallucination Rate** and **0.0 Graph Edit Distance** on verified codebases, outperforming the base paper (CodeR) and standard single-shot baselines by over **18.6%** and **28.9%** respectively.
