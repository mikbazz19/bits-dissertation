"""
ExtractionEvaluator – runs every extraction module against annotated ground
truth and returns per-module Precision / Recall / F1-Score.

Usage
-----
    from src.evaluation.evaluator import ExtractionEvaluator
    from src.evaluation.ground_truth import ALL_RESUME_ANNOTATIONS

    evaluator = ExtractionEvaluator()
    results = evaluator.evaluate_all(ALL_RESUME_ANNOTATIONS)
    print(results)          # formatted table
    print(results.to_dict())  # structured dict / JSON-serialisable
"""

from pathlib import Path
from typing import Dict, List, Optional

from ..data.parser import ResumeParser
from ..extraction.entity_extractor import EntityExtractor
from ..extraction.skill_extractor import SkillExtractor
from ..extraction.experience_extractor import ExperienceExtractor
from ..data.preprocessor import TextPreprocessor

from .ground_truth import ResumeAnnotation
from .metrics import (
    ExtractionMetrics,
    ModuleMetrics,
    compute_metrics,
    compute_single_value_metric,
)


class ExtractionEvaluator:
    """
    Evaluate all extraction modules against manually annotated resumes.

    For each annotation in the supplied list the evaluator:
      1. Reads the raw resume file (or uses cached text).
      2. Runs every extractor.
      3. Compares predictions to ground-truth labels using TP/FP/FN logic.
      4. Accumulates counts across all resumes before computing final metrics.

    Accumulated counts (not per-resume averages) are used so that the final
    metrics reflect corpus-level behaviour, which is the standard in NLP
    evaluation literature.
    """

    def __init__(self) -> None:
        self._parser      = ResumeParser()
        self._entities    = EntityExtractor()
        self._skills      = SkillExtractor()
        self._experience  = ExperienceExtractor()
        self._preprocessor = TextPreprocessor()

    # ── Public API ────────────────────────────────────────────────────────

    def evaluate_all(
        self, annotations: List[ResumeAnnotation]
    ) -> ExtractionMetrics:
        """
        Run all extraction modules over every annotated resume and return
        aggregated ExtractionMetrics.
        """
        # Accumulators: module_name → [tp, fp, fn]
        accum: Dict[str, List[int]] = {}

        for ann in annotations:
            resume_text = self._load_text(ann)
            if not resume_text:
                continue

            per_resume = self._evaluate_one(resume_text, ann)
            for m in per_resume:
                if m.module not in accum:
                    accum[m.module] = [0, 0, 0]
                accum[m.module][0] += m.true_positives
                accum[m.module][1] += m.false_positives
                accum[m.module][2] += m.false_negatives

        results = ExtractionMetrics()
        for module_name, (tp, fp, fn) in accum.items():
            results.add(ModuleMetrics(module_name, tp, fp, fn))
        return results

    def evaluate_single(
        self, annotation: ResumeAnnotation
    ) -> ExtractionMetrics:
        """Evaluate a single annotated resume."""
        resume_text = self._load_text(annotation)
        if not resume_text:
            return ExtractionMetrics()

        results = ExtractionMetrics()
        for m in self._evaluate_one(resume_text, annotation):
            results.add(m)
        return results

    # ── Internal helpers ──────────────────────────────────────────────────

    def _load_text(self, ann: ResumeAnnotation) -> Optional[str]:
        """Load resume text from file."""
        try:
            return self._parser.parse_file(ann.file_path)
        except Exception as e:
            print(f"  [WARN] Could not load {ann.file_path}: {e}")
            return None

    def _evaluate_one(
        self, resume_text: str, ann: ResumeAnnotation
    ) -> List[ModuleMetrics]:
        """Run all extractors on one resume and return per-module metrics."""
        metrics: List[ModuleMetrics] = []

        # ── 1. Email ──────────────────────────────────────────────────────
        from ..utils.helpers import extract_email
        pred_email = extract_email(resume_text)
        metrics.append(
            compute_single_value_metric("Email Extraction", pred_email, ann.email)
        )

        # ── 2. Phone ──────────────────────────────────────────────────────
        from ..utils.helpers import extract_phone
        pred_phone = extract_phone(resume_text)
        # Normalise: strip non-digit chars for comparison
        def _digits(s: Optional[str]) -> str:
            return "".join(c for c in (s or "") if c.isdigit())
        pred_phone_norm  = _digits(pred_phone)
        truth_phone_norm = _digits(ann.phone)
        metrics.append(
            compute_single_value_metric(
                "Phone Extraction",
                pred_phone_norm,
                truth_phone_norm,
                normalise=False,
            )
        )

        # ── 3. Name ───────────────────────────────────────────────────────
        entities = self._entities.extract_all_entities(resume_text)
        pred_name = entities.get("name")
        metrics.append(
            compute_single_value_metric("Name Extraction", pred_name, ann.name)
        )

        # ── 4. Skill Extraction ───────────────────────────────────────────
        pred_skills = self._skills.extract_skills(resume_text)
        metrics.append(
            compute_metrics("Skill Extraction", pred_skills, ann.skills, normalise=True)
        )

        # ── 5. Experience Extraction ──────────────────────────────────────
        # Pass full resume text so the block-based extractor can scan the whole
        # document; the preprocessor's section splitter is unreliable here.
        pred_experiences = self._experience.extract_experience(resume_text)
        pred_exp_titles = [e.title for e in pred_experiences]
        truth_exp_titles = [e["title"] for e in ann.experience_entries]
        metrics.append(
            compute_metrics(
                "Experience Extraction",
                pred_exp_titles,
                truth_exp_titles,
                normalise=False,
            )
        )

        # ── 6. Education Extraction ───────────────────────────────────────
        pred_education = entities.get("education", [])
        pred_degrees   = [e.get("degree", "") for e in pred_education]
        metrics.append(
            compute_metrics(
                "Education Extraction",
                pred_degrees,
                ann.education_degrees,
                normalise=False,
            )
        )

        # ── 7. Certification Extraction ───────────────────────────────────
        pred_certs = entities.get("certifications", [])
        metrics.append(
            compute_metrics(
                "Certification Extraction",
                pred_certs,
                ann.certifications,
                normalise=False,
            )
        )

        return metrics
