"""Skill gap analysis"""

import re
from typing import Dict, List
from ..models.resume import Resume
from ..models.job import JobDescription
from ..utils.helpers import normalize_skill, calculate_experience_years


class GapAnalyzer:
    """Analyze skill and qualification gaps"""
    
    def analyze_gaps(self, resume: Resume, job: JobDescription) -> Dict:
        """Comprehensive gap analysis"""
        
        skill_gaps = self._analyze_skill_gaps(resume, job)
        experience_gaps = self._analyze_experience_gaps(resume, job)
        education_gaps = self._analyze_education_gaps(resume, job)
        
        # Generate improvement suggestions
        suggestions = self._generate_suggestions(skill_gaps, experience_gaps, education_gaps)
        
        return {
            'skill_gaps': skill_gaps,
            'experience_gaps': experience_gaps,
            'education_gaps': education_gaps,
            'improvement_suggestions': suggestions,
            'priority_areas': self._identify_priority_areas(skill_gaps, experience_gaps)
        }
    
    def _analyze_skill_gaps(self, resume: Resume, job: JobDescription) -> Dict:
        """Analyze skill gaps"""
        resume_skills_norm = set(normalize_skill(s) for s in resume.skills)
        
        # Required skills analysis
        required_skills_norm = [normalize_skill(s) for s in job.required_skills]
        missing_required = [
            job.required_skills[i] for i, s in enumerate(required_skills_norm)
            if s not in resume_skills_norm
        ]
        
        # Preferred skills analysis
        preferred_skills_norm = [normalize_skill(s) for s in job.preferred_skills]
        missing_preferred = [
            job.preferred_skills[i] for i, s in enumerate(preferred_skills_norm)
            if s not in resume_skills_norm
        ]
        
        # Calculate coverage
        required_coverage = (len(job.required_skills) - len(missing_required)) / len(job.required_skills) * 100 if job.required_skills else 100
        preferred_coverage = (len(job.preferred_skills) - len(missing_preferred)) / len(job.preferred_skills) * 100 if job.preferred_skills else 100
        
        return {
            'missing_required_skills': missing_required,
            'missing_preferred_skills': missing_preferred,
            'required_skills_coverage': round(required_coverage, 2),
            'preferred_skills_coverage': round(preferred_coverage, 2),
            'total_missing': len(missing_required) + len(missing_preferred)
        }
    
    def _calculate_relevant_experience(self, resume: Resume, job: JobDescription) -> float:
        """
        Sum experience years from roles relevant to the job's domain.
        Builds domain keywords from job title + required skills + job description.
        """
        if not resume.experience:
            return 0.0

        stop_words = {'and', 'the', 'for', 'with', 'senior', 'junior', 'lead',
                      'staff', 'principal', 'mid', 'level', 'role', 'position',
                      'company', 'location', 'about', 'our', 'you', 'will', 'join'}
        domain_words: set = set()

        # From job title
        for token in re.split(r'\W+', job.title.lower()):
            if len(token) > 2 and token not in stop_words:
                domain_words.add(token)

        # From required skills (most reliable signal)
        for skill in job.required_skills[:15]:
            for token in re.split(r'\W+', skill.lower()):
                if len(token) > 2 and token not in stop_words:
                    domain_words.add(token)

        # From first 500 chars of job description (captures role context)
        desc_snippet = job.description[:500].lower()
        for token in re.split(r'\W+', desc_snippet):
            # Only add longer, likely-meaningful words
            if len(token) > 4 and token not in stop_words:
                domain_words.add(token)

        relevant_years = 0.0
        for exp in resume.experience:
            haystack = f"{exp.title} {exp.description}".lower()
            if any(kw in haystack for kw in domain_words):
                relevant_years += calculate_experience_years(exp.duration)

        return round(relevant_years, 1)

    def _analyze_experience_gaps(self, resume: Resume, job: JobDescription) -> Dict:
        """Analyze experience gaps using domain-relevant experience."""
        required_exp = job.required_experience
        total_exp = resume.total_experience_years
        relevant_exp = min(self._calculate_relevant_experience(resume, job), total_exp)

        # Use relevant experience for the gap; fall back to total if no relevant found
        effective_exp = relevant_exp if relevant_exp > 0 else total_exp
        gap = max(0, required_exp - effective_exp)
        meets_requirement = effective_exp >= required_exp

        return {
            'job_domain': job.title,
            'required_experience': required_exp,
            'relevant_experience': relevant_exp,
            'total_experience': total_exp,
            # kept for backward compat
            'candidate_experience': effective_exp,
            'experience_gap_years': round(gap, 1),
            'meets_requirement': meets_requirement,
            'percentage_of_requirement': round(
                (effective_exp / required_exp * 100) if required_exp > 0 else 100, 2
            )
        }
    
    def _analyze_education_gaps(self, resume: Resume, job: JobDescription) -> Dict:
        """Analyze education gaps"""
        if not job.education_requirements:
            return {
                'meets_requirement': True,
                'missing_qualifications': [],
                'message': "No specific education requirements"
            }
        
        resume_degrees = [edu.degree.lower() for edu in resume.education]
        
        # Check each requirement
        missing = []
        for req in job.education_requirements:
            req_lower = req.lower()
            matched = False
            
            for degree in resume_degrees:
                if req_lower in degree or degree in req_lower:
                    matched = True
                    break
            
            if not matched:
                missing.append(req)
        
        return {
            'meets_requirement': len(missing) == 0,
            'missing_qualifications': missing,
            'message': "All requirements met" if not missing else f"Missing {len(missing)} qualification(s)"
        }
    
    def _generate_suggestions(self, skill_gaps: Dict, experience_gaps: Dict, education_gaps: Dict) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        # Skill-based suggestions
        if skill_gaps['missing_required_skills']:
            top_missing = skill_gaps['missing_required_skills'][:5]
            suggestions.append(f"Priority: Learn these critical skills - {', '.join(top_missing)}")
            suggestions.append("Consider online courses, certifications, or bootcamps for quick skill acquisition")
        
        if skill_gaps['missing_preferred_skills']:
            suggestions.append(f"Consider learning preferred skills: {', '.join(skill_gaps['missing_preferred_skills'][:3])}")
        
        # Experience-based suggestions
        if not experience_gaps['meets_requirement']:
            gap_years = experience_gaps['experience_gap_years']
            domain = experience_gaps.get('job_domain', 'this role')
            if gap_years > 2:
                suggestions.append(
                    f"Gain {gap_years:.1f} more years of relevant experience in {domain}"
                )
                suggestions.append("Consider internships, freelance projects, or entry-level positions to build experience")
            else:
                suggestions.append("Highlight relevant projects and transferable skills to compensate for experience gap")
        
        # Education-based suggestions
        if not education_gaps['meets_requirement']:
            missing_quals = education_gaps['missing_qualifications']
            suggestions.append(f"Consider pursuing: {', '.join(missing_quals)}")
            suggestions.append("Look for part-time or online degree programs if currently employed")
        
        # General suggestions
        if not suggestions:
            suggestions.append("Strong candidate! Focus on highlighting your relevant experience and skills")
            suggestions.append("Consider adding any missing preferred skills to strengthen your profile")
        
        return suggestions
    
    def _identify_priority_areas(self, skill_gaps: Dict, experience_gaps: Dict) -> List[str]:
        """Identify priority improvement areas"""
        priority = []
        
        # Critical skill gaps
        if len(skill_gaps['missing_required_skills']) > 3:
            priority.append("Critical Skill Gaps")
        
        # Experience shortfall (based on relevant experience)
        if experience_gaps['experience_gap_years'] > 1:
            priority.append("Experience Requirement")
        
        # Some missing skills but not critical
        if skill_gaps['required_skills_coverage'] < 70:
            priority.append("Skill Development")
        
        if not priority:
            priority.append("Minor Improvements")
        
        return priority
    
    def generate_learning_path(self, missing_skills: List[str]) -> List[Dict]:
        """Generate a learning path for missing skills"""
        learning_resources = {
            'python': {'type': 'Course', 'platform': 'Coursera/Udemy', 'duration': '4-8 weeks'},
            'java': {'type': 'Course', 'platform': 'Oracle/Coursera', 'duration': '6-10 weeks'},
            'machine learning': {'type': 'Course', 'platform': 'Coursera/fast.ai', 'duration': '12-16 weeks'},
            'aws': {'type': 'Certification', 'platform': 'AWS Training', 'duration': '8-12 weeks'},
            'docker': {'type': 'Tutorial', 'platform': 'Docker Docs/YouTube', 'duration': '2-4 weeks'},
            'kubernetes': {'type': 'Course', 'platform': 'Linux Academy/Udemy', 'duration': '6-8 weeks'},
        }
        
        learning_path = []
        for skill in missing_skills[:10]:  # Limit to top 10
            skill_lower = normalize_skill(skill)
            
            # Check if we have specific recommendation
            resource = learning_resources.get(skill_lower, {
                'type': 'Online Course/Tutorial',
                'platform': 'Udemy/Coursera/YouTube',
                'duration': '2-8 weeks'
            })
            
            learning_path.append({
                'skill': skill,
                'type': resource['type'],
                'platform': resource['platform'],
                'estimated_duration': resource['duration']
            })
        
        return learning_path
