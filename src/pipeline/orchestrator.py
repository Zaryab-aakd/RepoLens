"""Multi-agent orchestrator implementing the closed-loop AST self-correction pipeline."""

import json
from pathlib import Path
from typing import Optional
from src.agents.scanner_agent import ScannerAgent
from src.agents.synthesizer_agent import SynthesizerAgent
from src.agents.verifier_agent import VerifierAgent
from src.config import SystemConfig
from src.logger import TrajectoryLogger
from src.models import (
    RepoLensOutput,
    VerificationReport
)


class RepoLensOrchestrator:
    """Coordinates Scanner, Synthesizer, and Verifier agents in an iterative closed-loop pipeline."""

    def __init__(self, config: Optional[SystemConfig] = None):
        self.config = config or SystemConfig()

    def run(self, repo_path: Path, repo_name: Optional[str] = None) -> RepoLensOutput:
        repo_path = repo_path.resolve()
        name = repo_name or repo_path.name
        logger = TrajectoryLogger(repo_name=name, logs_dir=self.config.logs_dir)

        logger.log_step(
            agent_role="Orchestrator",
            action="pipeline_start",
            thought=f"Starting RepoLens pipeline for '{name}' with ablation flags: "
                    f"ScannerMatrix={self.config.ablation.enable_scanner_matrix}, "
                    f"ASTVerification={self.config.ablation.enable_ast_verification}, "
                    f"ProgrammaticMermaid={self.config.ablation.enable_programmatic_mermaid}.",
            input_payload={"repo_path": str(repo_path), "repo_name": name}
        )

        scanner = ScannerAgent(self.config, logger)
        synthesizer = SynthesizerAgent(self.config, logger)
        verifier = VerifierAgent(self.config, logger)

        # 1. Phase 1: Codebase Scanning & AST Matrix Extraction
        scan_data = scanner.scan(repo_path, name)
        repo_ast = scan_data["repo_ast"]

        # 2. Phase 2: Synthesis and Iterative Verification Loop
        iteration = 1
        feedback: Optional[VerificationReport] = None
        max_iters = self.config.ablation.max_correction_iterations if self.config.ablation.enable_ast_verification else 1

        readme_md = ""
        mermaid_code = ""
        report: Optional[VerificationReport] = None

        while iteration <= max_iters:
            # Synthesize draft
            draft = synthesizer.synthesize(scan_data, feedback=feedback, iteration=iteration)
            readme_md = draft["readme_markdown"]
            mermaid_code = draft["mermaid_diagram"]

            # If AST verification is ablated/disabled, terminate after initial draft
            if not self.config.ablation.enable_ast_verification:
                logger.log_step(
                    agent_role="Orchestrator",
                    action="skip_verification (Ablation)",
                    thought="AST verification loop is ablated. Outputting unverified synthesis."
                )
                # Compute verification report strictly for metric recording without self-correction
                report = verifier.verify(repo_ast, readme_md, mermaid_code)
                break

            # Run deterministic AST verification
            report = verifier.verify(repo_ast, readme_md, mermaid_code)

            if report.is_valid:
                logger.log_step(
                    agent_role="Orchestrator",
                    action="verification_passed",
                    thought=f"Iteration {iteration}: All claims verified with 0% hallucination rate. Terminating self-correction loop."
                )
                break
            else:
                logger.record_correction_iteration()
                logger.log_step(
                    agent_role="Orchestrator",
                    action="trigger_self_correction",
                    thought=f"Iteration {iteration}: Detected {report.total_hallucinations} hallucinations. Routing feedback to Synthesizer.",
                    input_payload={"iteration": iteration, "hallucinations": report.total_hallucinations}
                )
                feedback = report
                iteration += 1

        # Finalize and record trajectory
        trajectory = logger.finalize()

        output = RepoLensOutput(
            repo_name=name,
            readme_markdown=readme_md,
            mermaid_diagram=mermaid_code,
            verification_report=report or VerificationReport(is_valid=True, total_claims=0, verified_claims=0, total_hallucinations=0, hallucination_rate=0.0, precision=1.0, recall=1.0),
            trajectory=trajectory,
            iterations_used=iteration if iteration <= max_iters else max_iters,
            ablation_flags={
                "enable_scanner_matrix": self.config.ablation.enable_scanner_matrix,
                "enable_ast_verification": self.config.ablation.enable_ast_verification,
                "enable_programmatic_mermaid": self.config.ablation.enable_programmatic_mermaid,
                "is_multi_agent": self.config.ablation.is_multi_agent
            }
        )

        # Write artifacts to docs/<repo_name>/
        out_dir = self.config.get_output_dir(name)
        (out_dir / "README.md").write_text(output.readme_markdown, encoding="utf-8")
        (out_dir / "architecture.mmd").write_text(output.mermaid_diagram, encoding="utf-8")
        (out_dir / "verification_report.json").write_text(
            json.dumps(output.verification_report.model_dump(), indent=2),
            encoding="utf-8"
        )

        return output
