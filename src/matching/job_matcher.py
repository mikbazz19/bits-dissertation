"""Job matching logic to match resumes with job descriptions"""

from typing import Dict, List
from ..models.resume import Resume
from ..models.job import JobDescription
from ..utils.helpers import similarity_score, normalize_skill
from ..utils.config import Config
from .similarity import SimilarityCalculator


class JobMatcher:
    """Match candidate resumes with job descriptions"""
    
    def __init__(self):
        self.similarity_calc = SimilarityCalculator()
        self.skill_weight = Config.SKILLS_WEIGHT
        self.experience_weight = Config.EXPERIENCE_WEIGHT
        self.education_weight = Config.EDUCATION_WEIGHT
    
    def match_resume_to_job(self, resume: Resume, job: JobDescription) -> Dict:
        """Calculate match score between resume and job description"""
        
        # Calculate component scores
        skill_score = self._calculate_skill_match(resume, job)
        experience_score = self._calculate_experience_match(resume, job)
        education_score = self._calculate_education_match(resume, job)
        
        # Calculate weighted overall score
        overall_score = (
            skill_score * self.skill_weight +
            experience_score * self.experience_weight +
            education_score * self.education_weight
        )
        
        # Determine match level
        match_level = self._determine_match_level(overall_score)
        
        # Calculate skill gaps
        missing_skills = self._find_missing_skills(resume, job)
        
        return {
            'overall_score': round(overall_score * 100, 2),
            'skill_score': round(skill_score * 100, 2),
            'experience_score': round(experience_score * 100, 2),
            'education_score': round(education_score * 100, 2),
            'match_level': match_level,
            'missing_required_skills': missing_skills['required'],
            'missing_preferred_skills': missing_skills['preferred'],
            'matched_skills': missing_skills['matched'],
            'recommendation': self._generate_recommendation(overall_score, missing_skills)
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
    
    def _determine_match_level(self, score: float) -> str:
        """Determine match level based on score"""
        if score >= 0.8:
            return "Excellent Match"
        elif score >= 0.6:
            return "Good Match"
        elif score >= 0.4:
            return "Fair Match"
        else:
            return "Poor Match"
    
    def _generate_recommendation(self, score: float, missing_skills: Dict) -> str:
        """Generate recommendation based on match"""
        if score >= 0.8:
            return "Strong candidate. Recommend for interview."
        elif score >= 0.6:
            if len(missing_skills['required']) <= 2:
                return "Good candidate. Consider for interview with skill assessment."
            else:
                return "Candidate shows potential. May need training in key areas."
        elif score >= 0.4:
            return f"Below requirements. Missing {len(missing_skills['required'])} critical skills."
        else:
            return "Not recommended. Significant skill and experience gaps."
