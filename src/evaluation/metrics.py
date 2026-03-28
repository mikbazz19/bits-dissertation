"""
Core evaluation metrics for information extraction and matching quality.

Implements standard NLP evaluation metrics:
  - Precision  = TP / (TP + FP)
  - Recall     = TP / (TP + FN)
  - F1-Score   = 2 * P * R / (P + R)

Used to evaluate:
  - Entity extraction   (name, email, phone)
  - Skill extraction    (against annotated skill sets)
  - Experience extraction
  - Education extraction
  - Overall matching accuracy
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from ..utils.helpers import normalize_skill


# ─────────────────────────────────────────────────────────────────────────────
# Result containers
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ModuleMetrics:
    """Precision / Recall / F1 for a single extraction module."""
    module: str
    true_positives: int
    false_positives: int
    false_negatives: int

    @property
    def precision(self) -> float:
        denom = self.true_positives + self.false_positives
        return round(self.true_positives / denom, 4) if denom else 0.0

    @property
    def recall(self) -> float:
        denom = self.true_positives + self.false_negatives
        return round(self.true_positives / denom, 4) if denom else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return round(2 * p * r / (p + r), 4) if (p + r) else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "module":           self.module,
            "true_positives":   self.true_positives,
            "false_positives":  self.false_positives,
            "false_negatives":  self.false_negatives,
            "precision":        self.precision,
            "recall":           self.recall,
            "f1_score":         self.f1,
        }

    def __str__(self) -> str:  # noqa: D105
        return (
            f"{self.module:<28}  "
            f"P={self.precision:.2%}  "
            f"R={self.recall:.2%}  "
            f"F1={self.f1:.4f}  "
            f"(TP={self.true_positives}, FP={self.false_positives}, FN={self.false_negatives})"
        )


@dataclass
class ExtractionMetrics:
    """Aggregated extraction metrics across all modules."""
    per_module: List[ModuleMetrics] = field(default_factory=list)

    def add(self, m: ModuleMetrics) -> None:
        self.per_module.append(m)

    @property
    def macro_precision(self) -> float:
        if not self.per_module:
            return 0.0
        return round(sum(m.precision for m in self.per_module) / len(self.per_module), 4)

    @property
    def macro_recall(self) -> float:
        if not self.per_module:
            return 0.0
        return round(sum(m.recall for m in self.per_module) / len(self.per_module), 4)

    @property
    def macro_f1(self) -> float:
        p, r = self.macro_precision, self.macro_recall
        return round(2 * p * r / (p + r), 4) if (p + r) else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "per_module":       [m.to_dict() for m in self.per_module],
            "macro_precision":  self.macro_precision,
            "macro_recall":     self.macro_recall,
            "macro_f1":         self.macro_f1,
        }

    def __str__(self) -> str:
        lines = [
            "=" * 80,
            "EXTRACTION EVALUATION RESULTS",
            "=" * 80,
            f"{'Module':<28}  {'Precision':>10}  {'Recall':>8}  {'F1-Score':>10}",
            "-" * 80,
        ]
        for m in self.per_module:
            lines.append(
                f"{m.module:<28}  {m.precision:>10.2%}  {m.recall:>8.2%}  {m.f1:>10.4f}"
            )
        lines += [
            "-" * 80,
            f"{'Macro Average':<28}  {self.macro_precision:>10.2%}  "
            f"{self.macro_recall:>8.2%}  {self.macro_f1:>10.4f}",
            "=" * 80,
        ]
        return "\n".join(lines)


@dataclass
class MatchingMetrics:
    """Metrics for the job-matching engine."""
    # Binary shortlisting accuracy (system band ≥ Good == shortlisted vs recruiter truth)
    shortlist_correct: int = 0
    shortlist_total: int = 0

    # MAE between system score (0–100) and normalised recruiter score (0–100)
    score_absolute_errors: List[float] = field(default_factory=list)

    # Stored (system_rank, recruiter_rank) pairs for Spearman's rho
    rank_pairs: List[Tuple[int, int]] = field(default_factory=list)

    @property
    def shortlisting_accuracy(self) -> float:
        return (
            round(self.shortlist_correct / self.shortlist_total, 4)
            if self.shortlist_total
            else 0.0
        )

    @property
    def mean_absolute_error(self) -> float:
        return (
            round(sum(self.score_absolute_errors) / len(self.score_absolute_errors), 4)
            if self.score_absolute_errors
            else 0.0
        )

    @property
    def spearman_rho(self) -> Optional[float]:
        """Spearman's rank correlation coefficient."""
        if len(self.rank_pairs) < 2:
            return None
        n = len(self.rank_pairs)
        d_sq_sum = sum((s - r) ** 2 for s, r in self.rank_pairs)
        rho = 1 - (6 * d_sq_sum) / (n * (n ** 2 - 1))
        return round(rho, 4)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "shortlisting_accuracy": self.shortlisting_accuracy,
            "mean_absolute_error":   self.mean_absolute_error,
            "spearman_rho":          self.spearman_rho,
            "n_samples":             self.shortlist_total,
        }

    def __str__(self) -> str:
        rho = self.spearman_rho
        lines = [
            "=" * 50,
            "MATCHING ENGINE EVALUATION",
            "=" * 50,
            f"Shortlisting Accuracy : {self.shortlisting_accuracy:.2%}  "
            f"({self.shortlist_correct}/{self.shortlist_total})",
            f"Mean Absolute Error   : {self.mean_absolute_error:.2f} pts",
            f"Spearman's Rho (ρ)    : {rho if rho is not None else 'N/A (need ≥2 pairs)'}",
            "=" * 50,
        ]
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Core helper: compare predicted vs ground-truth token sets
# ─────────────────────────────────────────────────────────────────────────────

def _normalise_set(items: List[str], normalise: bool = True) -> Set[str]:
    """Return a lower-cased (and optionally normalised) set of strings."""
    if normalise:
        return {normalize_skill(i) for i in items if i}
    return {str(i).lower().strip() for i in items if i}


def compute_metrics(
    module_name: str,
    predicted: List[str],
    ground_truth: List[str],
    normalise: bool = True,
) -> ModuleMetrics:
    """
    Compute Precision, Recall, and F1-Score for a list-based extraction task.

    Parameters
    ----------
    module_name  : Human-readable name for the module being evaluated.
    predicted    : Items extracted by the system.
    ground_truth : Correct items from manual annotation.
    normalise    : Apply normalize_skill() before comparison (recommended for skills).

    Returns
    -------
    ModuleMetrics with TP, FP, FN, Precision, Recall, F1.
    """
    pred_set = _normalise_set(predicted, normalise)
    truth_set = _normalise_set(ground_truth, normalise)

    tp = len(pred_set & truth_set)
    fp = len(pred_set - truth_set)
    fn = len(truth_set - pred_set)

    return ModuleMetrics(
        module=module_name,
        true_positives=tp,
        false_positives=fp,
        false_negatives=fn,
    )


def compute_single_value_metric(
    module_name: str,
    predicted: Optional[str],
    ground_truth: Optional[str],
    normalise: bool = False,
) -> ModuleMetrics:
    """
    Compute TP/FP/FN for a single-value extraction (e.g., name, email, phone).

    - Both match   → TP=1, FP=0, FN=0
    - Predicted but wrong → TP=0, FP=1, FN=1
    - Not extracted       → TP=0, FP=0, FN=1
    - Extracted when none exists → TP=0, FP=1, FN=0
    """
    pred = (predicted or "").lower().strip()
    truth = (ground_truth or "").lower().strip()

    if not truth:
        # Nothing to find; penalise any spurious extraction
        return ModuleMetrics(module_name, 0, 1 if pred else 0, 0)
    if not pred:
        return ModuleMetrics(module_name, 0, 0, 1)
    if pred == truth:
        return ModuleMetrics(module_name, 1, 0, 0)
    return ModuleMetrics(module_name, 0, 1, 1)
