"""
evaluate.py – Standalone Evaluation Script
AI-Powered Resume Screening System
BITS Pilani – CCZG628T Dissertation

Runs all evaluation metrics described in Chapter 6 of the mid-semester
report (Mid_Semester_Report_AI_Resume_Screening.docx) and prints a
formatted results table.

Metrics computed
----------------
Extraction modules (Precision / Recall / F1-Score):
  • Email Extraction
  • Phone Extraction
  • Name Extraction
  • Skill Extraction
  • Experience Extraction
  • Education Extraction
  • Certification Extraction

Matching engine:
  • Shortlisting Accuracy
  • Mean Absolute Error (MAE)
  • Spearman's Rank Correlation (ρ)

Usage
-----
    python evaluate.py
    python evaluate.py --json          # output results as JSON
    python evaluate.py --save          # save results to temp/eval_results.json
"""

import sys
import json
import argparse
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent))

from src.evaluation.evaluator import ExtractionEvaluator
from src.evaluation.matching_evaluator import MatchingEvaluator
from src.evaluation.ground_truth import (
    ALL_RESUME_ANNOTATIONS,
    ALL_JOB_ANNOTATIONS,
    JOB_ANNOTATION_MAP,
)
from src.utils.config import Config


# ─────────────────────────────────────────────────────────────────────────────

def run_extraction_eval(verbose: bool = True) -> dict:
    """Run extraction module evaluation and return result dict."""
    print("\n" + "=" * 60)
    print("  STEP 1: EXTRACTION MODULE EVALUATION")
    print("=" * 60)
    print(f"  Evaluating on {len(ALL_RESUME_ANNOTATIONS)} annotated resume(s) …\n")

    evaluator = ExtractionEvaluator()
    results = evaluator.evaluate_all(ALL_RESUME_ANNOTATIONS)

    if verbose:
        print(results)   # formatted table from ExtractionMetrics.__str__
        print()

    return results.to_dict()


def run_matching_eval(verbose: bool = True) -> dict:
    """Run matching engine evaluation and return result dict."""
    print("=" * 60)
    print("  STEP 2: MATCHING ENGINE EVALUATION")
    print("=" * 60)
    n_pairs = sum(len(a.recruiter_decisions) for a in ALL_RESUME_ANNOTATIONS)
    print(f"  Evaluating on {n_pairs} (resume, job) pair(s) …\n")

    evaluator = MatchingEvaluator()
    results = evaluator.evaluate(
        ALL_RESUME_ANNOTATIONS,
        ALL_JOB_ANNOTATIONS,
        JOB_ANNOTATION_MAP,
    )

    if verbose:
        print(results)   # formatted table from MatchingMetrics.__str__
        print()

    return results.to_dict()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run AI Resume Screening System – Evaluation Metrics"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print results as JSON",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save results to temp/eval_results.json",
    )
    args = parser.parse_args()

    Config.ensure_directories()

    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║   AI Resume Screening System – Evaluation Report         ║")
    print("║   Precision / Recall / F1 / Matching Accuracy            ║")
    print("╚══════════════════════════════════════════════════════════╝")

    extraction_results = run_extraction_eval(verbose=not args.json)
    matching_results   = run_matching_eval(verbose=not args.json)

    combined = {
        "extraction": extraction_results,
        "matching":   matching_results,
    }

    if args.json:
        print(json.dumps(combined, indent=2))

    if args.save:
        out_path = Path("temp") / "eval_results.json"
        out_path.parent.mkdir(exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(combined, f, indent=2)
        print(f"\n  ✔  Results saved → {out_path}")

    # ── Summary ───────────────────────────────────────────────────────────
    if not args.json:
        print("=" * 60)
        print("  SUMMARY")
        print("=" * 60)
        macro = extraction_results.get("macro_f1", 0)
        mae   = matching_results.get("mean_absolute_error", 0)
        acc   = matching_results.get("shortlisting_accuracy", 0)
        rho   = matching_results.get("spearman_rho")
        print(f"  Extraction  Macro F1-Score       : {macro:.4f} ({macro:.2%})")
        print(f"  Matching   Shortlisting Accuracy : {acc:.2%}")
        print(f"  Matching   MAE (score points)    : {mae:.2f}")
        print(f"  Matching   Spearman's ρ          : {rho if rho is not None else 'N/A'}")
        print("=" * 60)
        print()


if __name__ == "__main__":
    main()
