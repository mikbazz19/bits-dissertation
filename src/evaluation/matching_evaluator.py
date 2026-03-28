"""
MatchingEvaluator – evaluates the job-matching engine against recruiter
reference decisions stored in the ground-truth annotations.

Metrics computed
----------------
1. Shortlisting Accuracy
   System predicts shortlist when match_level ∈ {Excellent Match, Good Match}.
   Accuracy = fraction of predictions that agree with recruiter ground truth.

2. Mean Absolute Error (MAE)
   |system_score – recruiter_score| averaged across all (resume, job) pairs.

3. Spearman's Rank Correlation (ρ)
   Measures whether the system's ranking order of candidates agrees with the
   recruiter's ranking order. Computed from rank pairs stored during evaluation.

Usage
-----
    from src.evaluation.matching_evaluator import MatchingEvaluator
    from src.evaluation.ground_truth import (
        ALL_RESUME_ANNOTATIONS, ANNOTATION_JOB_1, ANNOTATION_JOB_2,
        JOB_ANNOTATION_MAP,
    )

    evaluator = MatchingEvaluator()
    results = evaluator.evaluate(
        ALL_RESUME_ANNOTATIONS,
        [ANNOTATION_JOB_1, ANNOTATION_JOB_2],
        JOB_ANNOTATION_MAP,
    )
    print(results)
"""

from typing import Dict, List

from ..data.parser import ResumeParser
from ..data.preprocessor import TextPreprocessor
from ..extraction.entity_extractor import EntityExtractor
from ..extraction.skill_extractor import SkillExtractor
from ..extraction.experience_extractor import ExperienceExtractor
from ..matching.job_matcher import JobMatcher
from ..models.resume import Resume, Education, Experience
from ..models.job import JobDescription

from .ground_truth import JobAnnotation, ResumeAnnotation
from .metrics import MatchingMetrics

_SHORTLIST_LEVELS = {"Excellent Match", "Good Match"}


class MatchingEvaluator:
    """Evaluate JobMatcher against human-labelled recruiter decisions."""

    def __init__(self) -> None:
        self._parser       = ResumeParser()
        self._preprocessor = TextPreprocessor()
        self._entity_ext   = EntityExtractor()
        self._skill_ext    = SkillExtractor()
        self._exp_ext      = ExperienceExtractor()
        self._matcher      = JobMatcher()

    # ── Public API ────────────────────────────────────────────────────────

    def evaluate(
        self,
        resume_annotations: List[ResumeAnnotation],
        job_annotations: List[JobAnnotation],
        job_annotation_map: Dict[str, JobAnnotation],
    ) -> MatchingMetrics:
        """
        Run matching for every (resume, job) pair that has a recruiter decision
        and accumulate MatchingMetrics.
        """
        result = MatchingMetrics()

        # Collect (system_score, recruiter_score) across all pairs so we can
        # later derive Spearman's rho for ranking comparisons.
        all_pairs: List[tuple] = []  # (resume_id, job_id, sys_score, rec_score, sys_sl, rec_sl)

        for r_ann in resume_annotations:
            resume = self._build_resume(r_ann)
            if resume is None:
                continue

            for job_id, (rec_score, rec_shortlist) in r_ann.recruiter_decisions.items():
                j_ann = job_annotation_map.get(job_id)
                if j_ann is None:
                    continue

                job = self._build_job(j_ann)
                match = self._matcher.match_resume_to_job(resume, job)

                sys_score      = match["overall_score"]
                sys_shortlist  = match["match_level"] in _SHORTLIST_LEVELS

                # Shortlisting accuracy
                result.shortlist_total   += 1
                result.shortlist_correct += int(sys_shortlist == rec_shortlist)

                # MAE
                result.score_absolute_errors.append(abs(sys_score - rec_score))

                all_pairs.append(
                    (r_ann.resume_id, job_id, sys_score, rec_score, sys_shortlist, rec_shortlist)
                )

        # Spearman's rho – derive ranks from collected pairs
        # We rank by score within each job group.
        for j_ann in job_annotations:
            job_pairs = [(p[0], p[2], p[3]) for p in all_pairs if p[1] == j_ann.job_id]
            if len(job_pairs) < 2:
                continue
            sys_ranked = sorted(job_pairs, key=lambda x: x[1], reverse=True)
            rec_ranked = sorted(job_pairs, key=lambda x: x[2], reverse=True)
            sys_order  = {rid: rank + 1 for rank, (rid, _, _) in enumerate(sys_ranked)}
            rec_order  = {rid: rank + 1 for rank, (rid, _, _) in enumerate(rec_ranked)}
            for rid in sys_order:
                result.rank_pairs.append((sys_order[rid], rec_order.get(rid, 0)))

        return result

    # ── Helpers ───────────────────────────────────────────────────────────

    def _build_resume(self, ann: ResumeAnnotation) -> Resume | None:
        """Parse and extract a Resume object from the annotated file."""
        try:
            text = self._parser.parse_file(ann.file_path)
        except Exception as e:
            print(f"  [WARN] Could not parse {ann.file_path}: {e}")
            return None

        entities = self._entity_ext.extract_all_entities(text)
        skills   = self._skill_ext.extract_skills(text)
        sections = self._preprocessor.extract_sections(text)
        exps     = self._exp_ext.extract_experience(text, sections.get("experience", ""))
        total    = self._exp_ext.calculate_total_experience(exps) or \
                   self._exp_ext.extract_experience_summary(text) or 0.0

        edu_list = [
            Education(
                degree=e.get("degree", ""),
                institution=e.get("institution", "N/A"),
                year=e.get("year"),
            )
            for e in entities.get("education", [])
        ]

        return Resume(
            raw_text=text,
            name=entities.get("name"),
            email=entities.get("email"),
            phone=entities.get("phone"),
            skills=skills,
            education=edu_list,
            experience=exps,
            certifications=entities.get("certifications", []),
            total_experience_years=total,
        )

    def _build_job(self, ann: JobAnnotation) -> JobDescription:
        """Build a JobDescription object from a job annotation."""
        try:
            text = self._parser.parse_file(ann.file_path)
        except Exception:
            text = ann.title

        return JobDescription(
            title=ann.title,
            company="Annotated Reference",
            description=text,
            required_skills=ann.required_skills,
            preferred_skills=ann.preferred_skills,
            required_experience=ann.required_experience_years,
        )
