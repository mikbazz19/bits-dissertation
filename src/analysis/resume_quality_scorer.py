"""
Resume Quality Scorer Module
Evaluates resume quality based on completeness, formatting, and best practices
"""

import re
from typing import Dict, List, Tuple
from src.models.resume import Resume


class ResumeQualityScorer:
    """Scores resume quality across multiple dimensions"""

    def __init__(self):
        self.action_verbs = {
            'led', 'managed', 'developed', 'created', 'implemented', 'designed',
            'built', 'improved', 'increased', 'reduced', 'achieved', 'delivered',
            'launched', 'established', 'optimized', 'streamlined', 'transformed',
            'spearheaded', 'orchestrated', 'pioneered', 'drove', 'executed',
            'coordinated', 'facilitated', 'initiated', 'architected', 'automated'
        }

    def score_resume(self, resume: Resume, resume_text: str = "") -> Dict:
        """
        Calculate overall resume quality score with detailed breakdown

        Args:
            resume: Parsed Resume object
            resume_text: Original resume text for additional analysis

        Returns:
            Dict with overall score, component scores, and suggestions
        """
        scores = {}
        suggestions = []

        # 1. Completeness Score (0-25 points)
        completeness, comp_suggestions = self._score_completeness(resume)
        scores['completeness'] = completeness
        suggestions.extend(comp_suggestions)

        # 2. Content Quality Score (0-25 points)
        content_quality, content_suggestions = self._score_content_quality(resume, resume_text)
        scores['content_quality'] = content_quality
        suggestions.extend(content_suggestions)

        # 3. Skills Presentation Score (0-25 points)
        skills_score, skills_suggestions = self._score_skills_presentation(resume)
        scores['skills_presentation'] = skills_score
        suggestions.extend(skills_suggestions)

        # 4. Experience Quality Score (0-25 points)
        exp_score, exp_suggestions = self._score_experience_quality(resume, resume_text)
        scores['experience_quality'] = exp_score
        suggestions.extend(exp_suggestions)

        # Calculate overall score
        overall_score = sum(scores.values())

        # Determine grade
        grade = self._get_grade(overall_score)

        return {
            'overall_score': round(overall_score, 1),
            'grade': grade,
            'component_scores': scores,
            'suggestions': suggestions[:10],  # Limit to top 10 suggestions
            'strengths': self._identify_strengths(scores, resume),
            'max_score': 100
        }

    def _score_completeness(self, resume: Resume) -> Tuple[float, List[str]]:
        """Score based on presence of essential information"""
        score = 0
        suggestions = []
        max_score = 25

        # Contact information (10 points)
        if resume.email:
            score += 4
        else:
            suggestions.append("Add a professional email address")

        if resume.phone:
            score += 3
        else:
            suggestions.append("Add a phone number for contact")

        if resume.linkedin or resume.github:
            score += 3
        else:
            suggestions.append("Add LinkedIn or GitHub profile link")

        # Skills section (5 points)
        if resume.skills and len(resume.skills) >= 5:
            score += 5
        elif resume.skills:
            score += 2
            suggestions.append(f"List more relevant skills (currently {len(resume.skills)})")
        else:
            suggestions.append("Add a skills section with relevant technical/professional skills")

        # Education (5 points)
        if resume.education and len(resume.education) > 0:
            score += 5
        else:
            suggestions.append("Add education information")

        # Experience (5 points)
        if resume.total_experience_years > 0:
            score += 5
        else:
            suggestions.append("Add work experience or relevant projects")

        return (score / max_score) * 25, suggestions

    def _score_content_quality(self, resume: Resume, resume_text: str) -> Tuple[float, List[str]]:
        """Score based on content quality indicators"""
        score = 0
        suggestions = []
        max_score = 25

        # Fall back to the resume's own raw text if no explicit text was supplied
        if not resume_text and resume.raw_text:
            resume_text = resume.raw_text

        # Check for quantified achievements (10 points)
        if resume_text:
            # Look for numbers/percentages in text
            numbers = re.findall(r'\d+%|\d+\+|increased|decreased|reduced|improved', resume_text.lower())
            if len(numbers) >= 5:
                score += 10
            elif len(numbers) >= 2:
                score += 5
                suggestions.append("Add more quantified achievements (e.g., 'Increased efficiency by 30%')")
            else:
                suggestions.append("Quantify your achievements with numbers and percentages")

        # Check for action verbs (10 points)
        if resume_text:
            text_lower = resume_text.lower()
            action_verb_count = sum(1 for verb in self.action_verbs if verb in text_lower)
            if action_verb_count >= 8:
                score += 10
            elif action_verb_count >= 4:
                score += 6
                suggestions.append("Use more strong action verbs (led, developed, implemented, etc.)")
            else:
                suggestions.append("Start bullet points with strong action verbs")

        # Resume length check (5 points)
        if resume_text:
            word_count = len(resume_text.split())
            if 300 <= word_count <= 800:
                score += 5
            elif word_count < 300:
                suggestions.append("Resume appears too brief - add more detail about achievements")
            else:
                suggestions.append("Resume may be too long - focus on most relevant experiences")

        return (score / max_score) * 25, suggestions

    def _score_skills_presentation(self, resume: Resume) -> Tuple[float, List[str]]:
        """Score based on skills section quality"""
        score = 0
        suggestions = []
        max_score = 25

        if not resume.skills:
            suggestions.append("Add a skills section to your resume")
            return 0, suggestions

        # Number of skills (10 points)
        skill_count = len(resume.skills)
        if skill_count >= 10:
            score += 10
        elif skill_count >= 5:
            score += 7
        else:
            score += 4
            suggestions.append(f"Add more relevant skills (currently {skill_count})")

        # Skills diversity (10 points) - check if skills span multiple categories
        skills_text = ' '.join(resume.skills).lower()
        categories_found = 0

        if any(lang in skills_text for lang in ['python', 'java', 'javascript', 'c++', 'c#', 'go', 'ruby', 'php']):
            categories_found += 1

        if any(tool in skills_text for tool in ['git', 'docker', 'kubernetes', 'jenkins', 'aws', 'azure', 'gcp']):
            categories_found += 1

        if any(db in skills_text for db in ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'database']):
            categories_found += 1

        if any(fw in skills_text for fw in ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express']):
            categories_found += 1

        score += min(categories_found * 2.5, 10)

        if categories_found < 2:
            suggestions.append("Include skills from multiple categories (languages, frameworks, tools)")

        # Certifications bonus (5 points)
        if resume.certifications and len(resume.certifications) > 0:
            score += 5
        else:
            suggestions.append("Consider adding relevant certifications if you have any")

        return (score / max_score) * 25, suggestions

    def _score_experience_quality(self, resume: Resume, resume_text: str) -> Tuple[float, List[str]]:
        """Score based on experience presentation"""
        score = 0
        suggestions = []
        max_score = 25

        # Years of experience (10 points)
        years = resume.total_experience_years
        if years >= 3:
            score += 10
        elif years >= 1:
            score += 7
        elif years > 0:
            score += 4
        else:
            suggestions.append("If you're a fresher, highlight internships, projects, or academic work")

        # Education quality (10 points)
        if resume.education:
            edu_count = len(resume.education)
            if edu_count >= 1:
                score += 5

            # Check if education has complete information
            complete_edu = sum(1 for edu in resume.education
                             if edu.degree and edu.institution)
            if complete_edu >= 1:
                score += 5
            else:
                suggestions.append("Include institution name and degree for education entries")

        # Projects/Activities (5 points)
        if resume.co_curricular_activities and len(resume.co_curricular_activities) > 0:
            score += 5
        else:
            suggestions.append("Add co-curricular activities or project experience")

        return (score / max_score) * 25, suggestions

    def _get_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return "A+ (Excellent)"
        elif score >= 80:
            return "A (Very Good)"
        elif score >= 70:
            return "B+ (Good)"
        elif score >= 60:
            return "B (Fair)"
        elif score >= 50:
            return "C (Needs Improvement)"
        else:
            return "D (Significant Improvement Needed)"

    def _identify_strengths(self, scores: Dict[str, float], resume: Resume) -> List[str]:
        """Identify resume strengths based on high scores"""
        strengths = []

        if scores['completeness'] >= 20:
            strengths.append("Complete contact and basic information")

        if scores['content_quality'] >= 18:
            strengths.append("Well-written content with quantified achievements")

        if scores['skills_presentation'] >= 18:
            strengths.append("Comprehensive and diverse skill set")

        if scores['experience_quality'] >= 18:
            strengths.append("Strong experience and education background")

        if resume.certifications and len(resume.certifications) > 0:
            strengths.append(f"Professional certifications ({len(resume.certifications)})")

        if resume.total_experience_years >= 5:
            strengths.append(f"Extensive experience ({resume.total_experience_years} years)")

        if not strengths:
            strengths.append("Room for improvement across all areas")

        return strengths
