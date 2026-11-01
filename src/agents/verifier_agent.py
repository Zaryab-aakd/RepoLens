"""Verifier Agent: Deterministic AST-grounded verification agent addressing Gap 2."""

import re
from typing import Dict, List, Set, Tuple
from src.agents.base_agent import BaseAgent
from src.config import SystemConfig
from src.graph.mermaid_generator import MermaidDiagramGenerator
from src.logger import TrajectoryLogger
from src.models import (
    FunctionSymbol,
    RepositoryAST,
    VerificationIssue,
    VerificationReport
)


class VerifierAgent(BaseAgent):
    """Deterministic AST-grounded verification agent addressing Gap 2."""

    FN_CLAIM_REGEX = re.compile(r'`([a-zA-Z0-9_.]+)\(([^)]*)\)(?:\s*->\s*([a-zA-Z0-9_\[\], ]+))?`')
    ROUTE_CLAIM_REGEX = re.compile(r'`\[(GET|POST|PUT|DELETE|PATCH)\]\s+([^`]+)`')

    def __init__(self, config: SystemConfig, logger: TrajectoryLogger):
        super().__init__("VerifierAgent", config, logger)

    def verify(
        self,
        repo_ast: RepositoryAST,
        readme_md: str,
        mermaid_code: str
    ) -> VerificationReport:
        self.log(
            action="verify_synthesis",
            thought="Executing deterministic AST cross-validation on synthesized Markdown and Mermaid topology."
        )

        issues: List[VerificationIssue] = []
        total_claims = 0
        verified_claims = 0

        # Build symbol lookups
        ast_functions = repo_ast.get_symbol_map()
        ast_files = set(repo_ast.files.keys())
        ast_routes: Dict[Tuple[str, str], FunctionSymbol] = {}
        for f in repo_ast.files.values():
            for fn in f.functions.values():
                if fn.is_route and fn.route_method and fn.route_path:
                    ast_routes[(fn.route_method.upper(), fn.route_path)] = fn

        # 1. Verify Function Signatures in Markdown
        for match in self.FN_CLAIM_REGEX.finditer(readme_md):
            fn_name = match.group(1)
            raw_args = match.group(2)
            claimed_args = [a.strip() for a in raw_args.split(",") if a.strip()]

            # Skip common generic markdown names
            if fn_name in {"classDef", "subgraph", "flowchart", "extends"}:
                continue

            total_claims += 1

            if fn_name not in ast_functions:
                # Ghost function hallucination
                issues.append(VerificationIssue(
                    claim=f"{fn_name}({raw_args})",
                    issue_type="ghost_function",
                    expected="Function defined in repository AST",
                    actual="Not found in AST symbol table",
                    description=f"Ghost function '{fn_name}' does not exist in any parsed repository file.",
                    suggested_correction=f"Remove '{fn_name}' or replace with actual repository function."
                ))
            else:
                actual_sym = ast_functions[fn_name]
                # Check parameters
                actual_args = actual_sym.arguments
                # Check if claimed parameters match actual parameters
                mismatched = False
                if claimed_args and actual_args:
                    for arg in claimed_args:
                        # strip default values or types if any
                        clean_arg = arg.split(":")[0].split("=")[0].strip()
                        if clean_arg and clean_arg not in actual_args and clean_arg != "...":
                            mismatched = True
                            break
                if mismatched:
                    issues.append(VerificationIssue(
                        claim=f"{fn_name}({raw_args})",
                        issue_type="signature_mismatch",
                        target_file=actual_sym.file_path,
                        expected=f"{fn_name}({', '.join(actual_args)})",
                        actual=f"{fn_name}({raw_args})",
                        description=f"Parameter mismatch for '{fn_name}'. Claimed ({raw_args}), AST has ({', '.join(actual_args)}).",
                        suggested_correction=f"Update signature to `{actual_sym.signature_str}`."
                    ))
                else:
                    verified_claims += 1

        # 2. Verify REST API Routes
        for match in self.ROUTE_CLAIM_REGEX.finditer(readme_md):
            method = match.group(1).upper()
            route_path = match.group(2).strip()
            total_claims += 1

            if (method, route_path) not in ast_routes:
                issues.append(VerificationIssue(
                    claim=f"[{method}] {route_path}",
                    issue_type="invalid_route",
                    expected="Route decorator present in AST",
                    actual="No matching endpoint found in AST",
                    description=f"HTTP endpoint [{method}] {route_path} is an unverified route hallucination.",
                    suggested_correction="Remove hallucinated route or update to match codebase endpoints."
                ))
            else:
                verified_claims += 1

        # 3. Verify Mermaid Diagram Nodes
        mermaid_nodes = MermaidDiagramGenerator.parse_mermaid_nodes(mermaid_code)
        for node_id in mermaid_nodes:
            total_claims += 1
            # Check if node corresponds to an actual file
            matched = any(MermaidDiagramGenerator._sanitize_id(f) == node_id for f in ast_files)
            if not matched and not node_id.startswith("subgraph"):
                issues.append(VerificationIssue(
                    claim=f"Mermaid node: {node_id}",
                    issue_type="invalid_node",
                    expected="File path represented in AST",
                    actual="Nonexistent file node in diagram",
                    description=f"Mermaid diagram node '{node_id}' does not correspond to any repository module.",
                    suggested_correction=f"Prune invalid node '{node_id}' from architecture diagram."
                ))
            else:
                verified_claims += 1

        total_hallucinations = len(issues)
        hallucination_rate = (total_hallucinations / total_claims) if total_claims > 0 else 0.0
        precision = (verified_claims / total_claims) if total_claims > 0 else 1.0
        
        # Ground truth count
        ground_truth_total = len(ast_functions) + len(ast_routes) + len(ast_files)
        recall = (verified_claims / ground_truth_total) if ground_truth_total > 0 else 1.0

        is_valid = (total_hallucinations == 0)

        report = VerificationReport(
            is_valid=is_valid,
            total_claims=total_claims,
            verified_claims=verified_claims,
            total_hallucinations=total_hallucinations,
            hallucination_rate=round(hallucination_rate, 4),
            precision=round(precision, 4),
            recall=round(recall, 4),
            issues=issues,
            audit_notes=f"AST verification completed: {verified_claims}/{total_claims} claims verified ({total_hallucinations} hallucinations detected)."
        )

        self.log(
            action="verification_completed",
            thought=f"Deterministic verification finished: is_valid={is_valid}, HR={report.hallucination_rate:.2%}, precision={report.precision:.2%}.",
            output_payload={
                "is_valid": is_valid,
                "total_claims": total_claims,
                "hallucinations": total_hallucinations,
                "hallucination_rate": report.hallucination_rate
            }
        )
        return report
