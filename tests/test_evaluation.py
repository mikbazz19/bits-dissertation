"""
Tests for the evaluation metrics module.

Covers:
  - compute_metrics()             (token-set P/R/F1)
  - compute_single_value_metric() (single-value entity P/R/F1)
  - ModuleMetrics properties      (precision, recall, f1)
  - ExtractionMetrics aggregation (macro scores)
  - MatchingMetrics               (accuracy, MAE, Spearman's ρ)
  - ExtractionEvaluator           (end-to-end on sample resumes)
  - MatchingEvaluator             (end-to-end on sample pairs)
"""

import pytest

from src.evaluation.metrics import (
    ModuleMetrics,
    ExtractionMetrics,
    MatchingMetrics,
    compute_metrics,
    compute_single_value_metric,
)
from src.evaluation.ground_truth import (
    ANNOTATION_RESUME_1,
    ANNOTATION_RESUME_2,
    ANNOTATION_JOB_1,
    ANNOTATION_JOB_2,
    ALL_RESUME_ANNOTATIONS,
    ALL_JOB_ANNOTATIONS,
    JOB_ANNOTATION_MAP,
)
from src.evaluation.evaluator import ExtractionEvaluator
from src.evaluation.matching_evaluator import MatchingEvaluator


# ─────────────────────────────────────────────────────────────────────────────
# ModuleMetrics – unit tests
# ─────────────────────────────────────────────────────────────────────────────

class TestModuleMetrics:

    def test_perfect_extraction(self):
        m = ModuleMetrics("Test", true_positives=5, false_positives=0, false_negatives=0)
        assert m.precision == 1.0
        assert m.recall    == 1.0
        assert m.f1        == 1.0

    def test_zero_precision_and_recall(self):
        m = ModuleMetrics("Test", true_positives=0, false_positives=3, false_negatives=2)
        assert m.precision == 0.0
        assert m.recall    == 0.0
        assert m.f1        == 0.0

    def test_partial_match(self):
        # TP=3, FP=1, FN=2  →  P=0.75, R=0.60
        m = ModuleMetrics("Test", true_positives=3, false_positives=1, false_negatives=2)
        assert m.precision == pytest.approx(0.75, abs=1e-4)
        assert m.recall    == pytest.approx(0.60, abs=1e-4)
        expected_f1 = 2 * 0.75 * 0.60 / (0.75 + 0.60)
        assert m.f1        == pytest.approx(expected_f1, abs=1e-4)

    def test_no_predictions_no_truth(self):
        m = ModuleMetrics("Test", true_positives=0, false_positives=0, false_negatives=0)
        assert m.precision == 0.0
        assert m.recall    == 0.0
        assert m.f1        == 0.0

    def test_to_dict_keys(self):
        m = ModuleMetrics("Email", true_positives=1, false_positives=0, false_negatives=0)
        d = m.to_dict()
        for key in ("module", "precision", "recall", "f1_score",
                    "true_positives", "false_positives", "false_negatives"):
            assert key in d


# ─────────────────────────────────────────────────────────────────────────────
# compute_metrics – token-set comparison
# ─────────────────────────────────────────────────────────────────────────────

class TestComputeMetrics:

    def test_exact_match_single_skill(self):
        m = compute_metrics("Skills", ["Python"], ["Python"])
        assert m.precision == 1.0
        assert m.recall    == 1.0
        assert m.f1        == 1.0

    def test_case_insensitive(self):
        m = compute_metrics("Skills", ["python"], ["Python"])
        assert m.true_positives == 1
        assert m.false_positives == 0
        assert m.false_negatives == 0

    def test_missing_skill(self):
        m = compute_metrics("Skills", ["Python", "Java"], ["Python", "Java", "React"])
        assert m.false_negatives == 1
        assert m.recall == pytest.approx(2 / 3, abs=1e-4)

    def test_spurious_skill(self):
        m = compute_metrics("Skills", ["Python", "Cobol"], ["Python"])
        assert m.false_positives == 1
        assert m.precision == pytest.approx(0.5, abs=1e-4)

    def test_empty_predicted(self):
        m = compute_metrics("Skills", [], ["Python", "Java"])
        assert m.true_positives  == 0
        assert m.false_negatives == 2
        assert m.recall          == 0.0

    def test_empty_ground_truth(self):
        m = compute_metrics("Skills", ["Python"], [])
        assert m.true_positives  == 0
        assert m.false_positives == 1

    def test_full_skill_overlap(self):
        skills = ["Python", "React", "Docker", "AWS"]
        m = compute_metrics("Skills", skills, skills)
        assert m.f1 == 1.0


# ─────────────────────────────────────────────────────────────────────────────
# compute_single_value_metric – entity matching
# ─────────────────────────────────────────────────────────────────────────────

class TestComputeSingleValue:

    def test_correct_email(self):
        m = compute_single_value_metric("Email", "user@example.com", "user@example.com")
        assert m.true_positives == 1

    def test_wrong_email(self):
        m = compute_single_value_metric("Email", "wrong@x.com", "right@x.com")
        assert m.false_positives  == 1
        assert m.false_negatives  == 1
        assert m.true_positives   == 0

    def test_missing_email(self):
        m = compute_single_value_metric("Email", None, "right@x.com")
        assert m.false_negatives  == 1
        assert m.true_positives   == 0

    def test_spurious_when_none_expected(self):
        m = compute_single_value_metric("Email", "spurious@x.com", None)
        assert m.false_positives  == 1

    def test_no_prediction_no_truth(self):
        m = compute_single_value_metric("Email", None, None)
        assert m.true_positives  == 0
        assert m.false_positives == 0
        assert m.false_negatives == 0


# ─────────────────────────────────────────────────────────────────────────────
# ExtractionMetrics – aggregation
# ─────────────────────────────────────────────────────────────────────────────

class TestExtractionMetrics:

    def _perfect(self, name):
        return ModuleMetrics(name, true_positives=4, false_positives=0, false_negatives=0)

    def _half(self, name):
        # P=0.5, R=0.5 → F1=0.5
        return ModuleMetrics(name, true_positives=2, false_positives=2, false_negatives=2)

    def test_empty(self):
        em = ExtractionMetrics()
        assert em.macro_f1 == 0.0

    def test_single_perfect_module(self):
        em = ExtractionMetrics()
        em.add(self._perfect("Email"))
        assert em.macro_precision == 1.0
        assert em.macro_recall    == 1.0
        assert em.macro_f1        == 1.0

    def test_two_modules_macro(self):
        em = ExtractionMetrics()
        em.add(self._perfect("Email"))  # P=1.0, R=1.0, F1=1.0
        em.add(self._half("Skills"))    # P=0.5, R=0.5, F1=0.5
        # macro_P = (1.0+0.5)/2 = 0.75; macro_R = 0.75 → macro_F1 = 0.75
        assert em.macro_f1 == pytest.approx(0.75, abs=1e-3)

    def test_to_dict_contains_per_module(self):
        em = ExtractionMetrics()
        em.add(self._perfect("Email"))
        d = em.to_dict()
        assert "per_module" in d
        assert len(d["per_module"]) == 1


# ─────────────────────────────────────────────────────────────────────────────
# MatchingMetrics
# ─────────────────────────────────────────────────────────────────────────────

class TestMatchingMetrics:

    def test_perfect_shortlisting(self):
        mm = MatchingMetrics(shortlist_correct=4, shortlist_total=4)
        assert mm.shortlisting_accuracy == 1.0

    def test_partial_shortlisting(self):
        mm = MatchingMetrics(shortlist_correct=3, shortlist_total=5)
        assert mm.shortlisting_accuracy == pytest.approx(0.6, abs=1e-4)

    def test_zero_shortlist_total(self):
        mm = MatchingMetrics()
        assert mm.shortlisting_accuracy == 0.0

    def test_mae(self):
        mm = MatchingMetrics(score_absolute_errors=[10.0, 5.0, 15.0])
        assert mm.mean_absolute_error == pytest.approx(10.0, abs=1e-4)

    def test_spearman_perfect_agreement(self):
        mm = MatchingMetrics(rank_pairs=[(1, 1), (2, 2), (3, 3)])
        assert mm.spearman_rho == pytest.approx(1.0, abs=1e-4)

    def test_spearman_perfect_disagreement(self):
        mm = MatchingMetrics(rank_pairs=[(1, 3), (2, 2), (3, 1)])
        assert mm.spearman_rho == pytest.approx(-1.0, abs=1e-4)

    def test_spearman_needs_two_pairs(self):
        mm = MatchingMetrics(rank_pairs=[(1, 1)])
        assert mm.spearman_rho is None

    def test_to_dict_keys(self):
        mm = MatchingMetrics(shortlist_correct=2, shortlist_total=4,
                              score_absolute_errors=[5.0],
                              rank_pairs=[(1, 1), (2, 2)])
        d = mm.to_dict()
        for key in ("shortlisting_accuracy", "mean_absolute_error",
                    "spearman_rho", "n_samples"):
            assert key in d


# ─────────────────────────────────────────────────────────────────────────────
# Ground truth sanity checks
# ─────────────────────────────────────────────────────────────────────────────

class TestGroundTruth:

    def test_resume_1_fields(self):
        ann = ANNOTATION_RESUME_1
        assert ann.name  == "Jane Smith"
        assert ann.email == "jane.smith@email.com"
        assert len(ann.skills) > 10
        assert ann.total_experience_years == 6.0
        assert len(ann.experience_entries) == 3
        assert len(ann.certifications)     == 2

    def test_resume_2_fields(self):
        ann = ANNOTATION_RESUME_2
        assert ann.name  == "Michael Chen"
        assert ann.email == "michael.chen@techmail.com"
        assert ann.total_experience_years == pytest.approx(4.5, abs=0.1)
        assert len(ann.skills) > 10

    def test_job_1_has_required_skills(self):
        assert len(ANNOTATION_JOB_1.required_skills) > 5
        assert ANNOTATION_JOB_1.required_experience_years == 5.0

    def test_job_2_has_required_skills(self):
        assert len(ANNOTATION_JOB_2.required_skills) > 5
        assert ANNOTATION_JOB_2.required_experience_years == 3.0

    def test_recruiter_decisions_present(self):
        assert "job_1" in ANNOTATION_RESUME_1.recruiter_decisions
        assert "job_2" in ANNOTATION_RESUME_2.recruiter_decisions


# ─────────────────────────────────────────────────────────────────────────────
# End-to-end: ExtractionEvaluator on sample resumes
# ─────────────────────────────────────────────────────────────────────────────

class TestExtractionEvaluatorEndToEnd:

    def test_evaluate_resume_1(self):
        ev = ExtractionEvaluator()
        result = ev.evaluate_single(ANNOTATION_RESUME_1)

        assert len(result.per_module) > 0
        module_names = [m.module for m in result.per_module]
        assert "Email Extraction" in module_names
        assert "Skill Extraction" in module_names

    def test_email_f1_is_1_for_resume_1(self):
        ev = ExtractionEvaluator()
        result = ev.evaluate_single(ANNOTATION_RESUME_1)
        email_m = next(m for m in result.per_module if m.module == "Email Extraction")
        assert email_m.f1 == 1.0

    def test_skill_extraction_recall_nonzero(self):
        ev = ExtractionEvaluator()
        result = ev.evaluate_single(ANNOTATION_RESUME_1)
        skill_m = next(m for m in result.per_module if m.module == "Skill Extraction")
        # System must extract at least some skills
        assert skill_m.recall > 0.0

    def test_evaluate_all_returns_macro_metrics(self):
        ev = ExtractionEvaluator()
        result = ev.evaluate_all(ALL_RESUME_ANNOTATIONS)
        assert result.macro_f1 > 0.0
        assert 0.0 <= result.macro_precision <= 1.0
        assert 0.0 <= result.macro_recall    <= 1.0

    def test_aggregate_over_two_resumes(self):
        ev = ExtractionEvaluator()
        result = ev.evaluate_all(ALL_RESUME_ANNOTATIONS)
        assert len(result.per_module) > 0


# ─────────────────────────────────────────────────────────────────────────────
# End-to-end: MatchingEvaluator
# ─────────────────────────────────────────────────────────────────────────────

class TestMatchingEvaluatorEndToEnd:

    def test_evaluate_returns_metrics(self):
        ev = MatchingEvaluator()
        result = ev.evaluate(
            ALL_RESUME_ANNOTATIONS,
            ALL_JOB_ANNOTATIONS,
            JOB_ANNOTATION_MAP,
        )
        # 2 resumes × 2 jobs = 4 pairs
        assert result.shortlist_total == 4
        assert len(result.score_absolute_errors) == 4

    def test_shortlisting_accuracy_in_range(self):
        ev = MatchingEvaluator()
        result = ev.evaluate(
            ALL_RESUME_ANNOTATIONS,
            ALL_JOB_ANNOTATIONS,
            JOB_ANNOTATION_MAP,
        )
        assert 0.0 <= result.shortlisting_accuracy <= 1.0

    def test_mae_is_nonnegative(self):
        ev = MatchingEvaluator()
        result = ev.evaluate(
            ALL_RESUME_ANNOTATIONS,
            ALL_JOB_ANNOTATIONS,
            JOB_ANNOTATION_MAP,
        )
        assert result.mean_absolute_error >= 0.0
