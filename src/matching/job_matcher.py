"""Job matching logic to match resumes with job descriptions"""

from typing import Dict, List
from ..models.resume import Resume
from ..models.job import JobDescription
from ..utils.helpers import similarity_score, normalize_skill
from ..utils.config import Config
from .similarity import SimilarityCalculator


class JobMatcher:
    """Match candidate resumes with job descriptions"""

    def __init__(self, skill_weight: float = None, experience_weight: float = None,
                 education_weight: float = None):
        self.similarity_calc = SimilarityCalculator()
        # Allow caller to override weights; fall back to Config defaults
        self.skill_weight = skill_weight if skill_weight is not None else Config.SKILLS_WEIGHT
        self.experience_weight = experience_weight if experience_weight is not None else Config.EXPERIENCE_WEIGHT
        self.education_weight = education_weight if education_weight is not None else Config.EDUCATION_WEIGHT
    
    def match_resume_to_job(self, resume: Resume, job: JobDescription) -> Dict:
        """Calculate match score between resume and job description."""

        # Step 1: Hard filters
        hard_filter_results, hard_filters_passed = self._apply_hard_filters(resume, job)

        # Step 2: Component scores (always calculated for transparency)
        skill_score = self._calculate_skill_match(resume, job)
        experience_score = self._calculate_experience_match(resume, job)
        education_score = self._calculate_education_match(resume, job)

        # Step 3: Weighted overall
        overall_score = (
            skill_score * self.skill_weight +
            experience_score * self.experience_weight +
            education_score * self.education_weight
        )

        # Step 4: Confidence factor (penalises sparse resume data)
        confidence_factor = self._compute_confidence(resume)
        overall_score = overall_score * confidence_factor
        overall_pct = round(overall_score * 100, 2)

        # Step 5: Decision
        if not hard_filters_passed:
            decision = "Reject"
            decision_reason = self._hard_filter_failure_reason(hard_filter_results)
        elif overall_pct >= Config.ACCEPT_THRESHOLD:
            decision = "Accept"
            decision_reason = "Meets all requirements with a strong overall score."
        elif overall_pct >= Config.REVIEW_THRESHOLD:
            decision = "Review"
            decision_reason = "Moderate match — requires human review before final decision."
        else:
            decision = "Reject"
            decision_reason = (
                f"Overall score {overall_pct}% is below the acceptance threshold "
                f"({Config.REVIEW_THRESHOLD}%)."
            )

        match_level = self._determine_match_level(overall_score)
        missing_skills = self._find_missing_skills(resume, job)

        return {
            'overall_score': overall_pct,
            'skill_score': round(skill_score * 100, 2),
            'experience_score': round(experience_score * 100, 2),
            'education_score': round(education_score * 100, 2),
            'confidence_factor': confidence_factor,
            'hard_filter_results': hard_filter_results,
            'hard_filters_passed': hard_filters_passed,
            'decision': decision,
            'decision_reason': decision_reason,
            'match_level': match_level,
            'missing_required_skills': missing_skills['required'],
            'missing_preferred_skills': missing_skills['preferred'],
            'matched_skills': missing_skills['matched'],
            'recommendation': self._generate_recommendation(overall_pct, missing_skills, decision)
        }
    
    def rank_candidates(self, resumes: List[Resume], job: JobDescription) -> List[Dict]:
        """Rank multiple candidates for a job"""
        results = []
        
        for resume in resumes:
            match_result = self.match_resume_to_job(resume, job)
            results.append({
                'resume': resume,
                'match_result': match_result
            })
        
        # Sort by overall score
        results.sort(key=lambda x: x['match_result']['overall_score'], reverse=True)
        
        return results
    
    def _calculate_skill_match(self, resume: Resume, job: JobDescription) -> float:
        """Calculate skill match score"""
        if not resume.skills:
            return 0.0
        
        # Normalize skills
        resume_skills = [normalize_skill(s) for s in resume.skills]
        
        # Required skills match
        required_skills = [normalize_skill(s) for s in job.required_skills]
        required_match = len(set(resume_skills) & set(required_skills)) / len(required_skills) if required_skills else 0
        
        # Preferred skills match
        preferred_skills = [normalize_skill(s) for s in job.preferred_skills]
        preferred_match = len(set(resume_skills) & set(preferred_skills)) / len(preferred_skills) if preferred_skills else 0
        
        # Weighted combination (required skills weighted more)
        skill_score = (required_match * 0.7) + (preferred_match * 0.3)
        
        return min(skill_score, 1.0)
    
    def _calculate_experience_match(self, resume: Resume, job: JobDescription) -> float:
        """Calculate experience match score"""
        if job.required_experience == 0:
            return 1.0
        
        if resume.total_experience_years >= job.required_experience:
            # Full score if meets or exceeds requirement
            return 1.0
        else:
            # Partial score based on percentage of requirement met
            return resume.total_experience_years / job.required_experience
    
    def _calculate_education_match(self, resume: Resume, job: JobDescription) -> float:
        """Calculate education match score"""
        if not job.education_requirements:
            return 1.0
        
        if not resume.education:
            return 0.0
        
        # Check if any education entry matches requirements
        resume_degrees = [edu.degree.lower() for edu in resume.education]
        
        for req in job.education_requirements:
            req_lower = req.lower()
            for degree in resume_degrees:
                if req_lower in degree or degree in req_lower:
                    return 1.0
        
        # Partial match if has any degree
        return 0.5
    
    def _find_missing_skills(self, resume: Resume, job: JobDescription) -> Dict:
        """Identify missing skills"""
        resume_skills_norm = set(normalize_skill(s) for s in resume.skills)
        
        required_skills_norm = [normalize_skill(s) for s in job.required_skills]
        preferred_skills_norm = [normalize_skill(s) for s in job.preferred_skills]
        
        missing_required = [
            job.required_skills[i] for i, s in enumerate(required_skills_norm)
            if s not in resume_skills_norm
        ]
        
        missing_preferred = [
            job.preferred_skills[i] for i, s in enumerate(preferred_skills_norm)
            if s not in resume_skills_norm
        ]
        
        matched_required = [
            job.required_skills[i] for i, s in enumerate(required_skills_norm)
            if s in resume_skills_norm
        ]
        
        return {
            'required': missing_required,
            'preferred': missing_preferred,
            'matched': matched_required
        }
    
    def _apply_hard_filters(self, resume: Resume, job: JobDescription) -> tuple:
        """Check mandatory requirements before scoring."""
        results = {}

        # Filter 1: Minimum experience
        req_exp = job.required_experience or 0
        cand_exp = resume.total_experience_years or 0
        results['experience'] = {
            'label': 'Minimum Experience',
            'passed': (req_exp == 0) or (cand_exp >= req_exp),
            'detail': f"{cand_exp} yrs (required: {req_exp} yrs)"
        }

        # Filter 2: Mandatory skills (must match at least half of top-5 required skills)
        if job.required_skills:
            resume_skills_norm = set(normalize_skill(s) for s in resume.skills)
            top_req = job.required_skills[:5]
            matched = sum(1 for s in top_req if normalize_skill(s) in resume_skills_norm)
            min_match = max(1, (len(top_req) + 1) // 2)
            results['mandatory_skills'] = {
                'label': 'Mandatory Skills',
                'passed': matched >= min_match,
                'detail': f"{matched}/{len(top_req)} key required skills matched (min {min_match})"
            }
        else:
            results['mandatory_skills'] = {
                'label': 'Mandatory Skills',
                'passed': True,
                'detail': 'No required skills specified'
            }

        # Filter 3: Education (only if job explicitly requires it)
        if job.education_requirements:
            has_edu = bool(resume.education)
            results['education'] = {
                'label': 'Required Education',
                'passed': has_edu,
                'detail': 'Qualifying degree found' if has_edu else 'No qualifying degree found'
            }
        else:
            results['education'] = {
                'label': 'Required Education',
                'passed': True,
                'detail': 'No specific education required'
            }

        # Filter 4: Overqualification — reject if experience exceeds requirement by buffer
        if req_exp > 0:
            buffer = Config.OVERQUALIFICATION_YEARS_BUFFER
            overqualified = cand_exp > req_exp + buffer
            results['overqualification'] = {
                'label': 'Experience Fit',
                'passed': not overqualified,
                'detail': (
                    f"{cand_exp} yrs exceeds the role's requirement of {req_exp} yrs "
                    f"by more than {buffer} years — candidate may be overqualified."
                    if overqualified else
                    f"{cand_exp} yrs is within acceptable range for {req_exp} yrs required."
                )
            }
        else:
            results['overqualification'] = {
                'label': 'Experience Fit',
                'passed': True,
                'detail': 'No experience requirement specified'
            }

        all_passed = all(v['passed'] for v in results.values())
        return results, all_passed

    def _compute_confidence(self, resume: Resume) -> float:
        """Return a confidence factor (0–1) based on resume data completeness."""
        factor = 1.0
        if not resume.skills:
            factor *= 0.85
        if not resume.education:
            factor *= 0.95
        if resume.total_experience_years == 0:
            factor *= 0.90
        return round(factor, 3)

    def _hard_filter_failure_reason(self, results: Dict) -> str:
        reasons = []
        for v in results.values():
            if not v['passed']:
                reasons.append(v['detail'])
        return " | ".join(reasons) if reasons else "Eligibility check failed."

    def _determine_match_level(self, score: float) -> str:
        """Determine match level based on score."""
        pct = score * 100
        if pct >= Config.ACCEPT_THRESHOLD:
            return "Strong Match"
        elif pct >= Config.REVIEW_THRESHOLD:
            return "Moderate Match"
        else:
            return "Weak Match"

    def _generate_recommendation(self, score_pct: float, missing_skills: Dict, decision: str) -> str:
        """Generate recommendation based on decision."""
        if decision == "Accept":
            return "Strong candidate. Recommend for interview."
        elif decision == "Review":
            n = len(missing_skills['required'])
            if n:
                return f"Moderate fit. Review manually — missing {n} required skill(s)."
            return "Moderate fit. Recommend manual review before deciding."
        else:
            n = len(missing_skills['required'])
            if n:
                return f"Below requirements. Missing {n} critical skill(s). Not recommended."
            return f"Score {score_pct}% below threshold. Not recommended for this role."
