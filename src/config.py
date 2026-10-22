"""Configuration settings and ablation flags for RepoLens."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class AblationConfig:
    """Ablation toggles for experimental evaluation (E1 - E6)."""
    # Gap 1: Multi-Agent Scanner & Explicit Dependency Matrix
    enable_scanner_matrix: bool = True
    
    # Gap 2: Deterministic AST-Grounded Verification Agent & Self-Correction Feedback Loop
    enable_ast_verification: bool = True
    max_correction_iterations: int = 3
    
    # Gap 3: Programmatic AST-Grounded Topology Synthesis for Mermaid Diagrams
    enable_programmatic_mermaid: bool = True
    
    # LLM & Multi-Agent Mode
    is_multi_agent: bool = True  # False for baseline single-shot or uncoordinated pipelines


@dataclass
class SystemConfig:
    """Core configuration for RepoLens execution and inference."""
    # LLM Settings
    provider: str = os.getenv("REPOLENS_PROVIDER", "deterministic")  # "deterministic", "ollama", "openai", "gemini"
    model_name: str = os.getenv("REPOLENS_MODEL", "Qwen2.5-Coder-32B-Instruct")
    api_key: Optional[str] = os.getenv("REPOLENS_API_KEY", None)
    base_url: Optional[str] = os.getenv("REPOLENS_BASE_URL", "http://localhost:11434/v1")
    temperature: float = 0.2
    random_seed: int = 42

    # Paths
    project_root: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent / "data")
    logs_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent / "logs")
    results_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent / "results")

    # Ablation Flags
    ablation: AblationConfig = field(default_factory=AblationConfig)

    def get_output_dir(self, repo_name: str) -> Path:
        out = self.project_root / "docs" / repo_name
        out.mkdir(parents=True, exist_ok=True)
        return out
