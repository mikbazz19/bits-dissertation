"""
Analytics Module
Provides visualization and analytics for resume screening results
"""

from typing import Dict, List, Tuple
import numpy as np
from src.models.resume import Resume
from src.models.job import JobDescription


class ScreeningAnalytics:
    """Generate analytics for single and batch screening modes"""

    def __init__(self):
        self.skill_categories = {
            'Programming Languages': ['python', 'java', 'javascript', 'c++', 'c#', 'go', 'ruby', 'php', 'typescript', 'kotlin', 'swift', 'rust'],
            'Web Technologies': ['html', 'css', 'react', 'angular', 'vue', 'node', 'express', 'django', 'flask', 'spring'],
            'Databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'cassandra', 'dynamodb'],
            'Cloud & DevOps': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible'],
            'Data Science & ML': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy'],
            'Tools & Others': ['git', 'jira', 'linux', 'agile', 'scrum', 'rest api', 'graphql', 'microservices']
        }

    def analyze_single_resume(self, resume: Resume, match_result: Dict = None) -> Dict:
        """
        Generate analytics for a single resume

        Returns:
            Dict with categorized skills, experience breakdown, strengths/weaknesses
        """
        # Categorize skills
        skill_breakdown = self._categorize_skills(resume.skills)

        # Experience analysis
        experience_level = self._classify_experience_level(resume.total_experience_years)

        # Profile strengths and weaknesses
        strengths = []
        weaknesses = []

        if resume.total_experience_years >= 3:
            strengths.append(f"Solid experience ({resume.total_experience_years} years)")
        elif resume.total_experience_years < 1:
            weaknesses.append("Limited work experience")

        if len(resume.skills) >= 10:
            strengths.append(f"Diverse skill set ({len(resume.skills)} skills)")
        elif len(resume.skills) < 5:
            weaknesses.append("Limited skills listed")

        if resume.certifications and len(resume.certifications) > 0:
            strengths.append(f"Professional certifications ({len(resume.certifications)})")
        else:
            weaknesses.append("No certifications listed")

        if resume.education and len(resume.education) > 0:
            strengths.append("Education credentials present")
        else:
            weaknesses.append("No education information")

        # Contact completeness
        contact_score = sum([
            bool(resume.email),
            bool(resume.phone),
            bool(resume.linkedin or resume.github)
        ]) / 3 * 100

        return {
            'skill_breakdown': skill_breakdown,
            'total_skills': len(resume.skills),
            'experience_years': resume.total_experience_years,
            'experience_level': experience_level,
            'education_count': len(resume.education) if resume.education else 0,
            'certification_count': len(resume.certifications) if resume.certifications else 0,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'contact_completeness': round(contact_score, 1),
            'profile_summary': self._generate_profile_summary(resume)
        }

    def analyze_batch_resumes(self, resumes: List[Resume], match_results: Dict[int, Dict]) -> Dict:
        """
        Generate comparative analytics for multiple resumes

        Args:
            resumes: List of Resume objects
            match_results: Dict mapping resume index to match result

        Returns:
            Dict with aggregate statistics and comparisons
        """
        valid_resumes = [(i, r) for i, r in enumerate(resumes) if r is not None]

        if not valid_resumes:
            return {
                'total_candidates': 0,
                'error': 'No valid resumes to analyze'
            }

        # Score distribution
        scores = []
        decisions = {'Accept': 0, 'Review': 0, 'Reject': 0}

        for idx, resume in valid_resumes:
            if idx in match_results:
                score = match_results[idx].get('overall_score', 0)
                scores.append(score)
                decision = match_results[idx].get('decision', 'Unknown')
                if decision in decisions:
                    decisions[decision] += 1

        # Experience distribution
        experience_levels = {'Entry Level (0-2 years)': 0, 'Mid Level (2-5 years)': 0,
                           'Senior Level (5+ years)': 0}
        total_experience = []

        for idx, resume in valid_resumes:
            exp = resume.total_experience_years
            total_experience.append(exp)
            if exp < 2:
                experience_levels['Entry Level (0-2 years)'] += 1
            elif exp < 5:
                experience_levels['Mid Level (2-5 years)'] += 1
            else:
                experience_levels['Senior Level (5+ years)'] += 1

        # Skill analysis
        all_skills = []
        for idx, resume in valid_resumes:
            all_skills.extend([s.lower() for s in resume.skills])

        skill_frequency = {}
        for skill in all_skills:
            skill_frequency[skill] = skill_frequency.get(skill, 0) + 1

        # Top skills
        top_skills = sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)[:10]

        # Common missing skills across resumes
        common_gaps = self._find_common_gaps(valid_resumes, match_results)

        return {
            'total_candidates': len(valid_resumes),
            'score_distribution': {
                'scores': scores,
                'mean': round(np.mean(scores), 1) if scores else 0,
                'median': round(np.median(scores), 1) if scores else 0,
                'std': round(np.std(scores), 1) if scores else 0,
                'min': round(min(scores), 1) if scores else 0,
                'max': round(max(scores), 1) if scores else 0
            },
            'decisions': decisions,
            'experience_distribution': experience_levels,
            'experience_stats': {
                'mean': round(np.mean(total_experience), 1) if total_experience else 0,
                'median': round(np.median(total_experience), 1) if total_experience else 0,
                'min': round(min(total_experience), 1) if total_experience else 0,
                'max': round(max(total_experience), 1) if total_experience else 0
            },
            'top_skills': top_skills,
            'common_missing_skills': common_gaps[:10],
            'avg_skills_per_candidate': round(len(all_skills) / len(valid_resumes), 1) if valid_resumes else 0
        }

    def _categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills into predefined categories"""
        categorized = {category: [] for category in self.skill_categories.keys()}
        uncategorized = []

        if not skills:
            return categorized

        skills_lower = [s.lower() for s in skills]

        for skill in skills:
            skill_lower = skill.lower()
            categorized_flag = False

            for category, keywords in self.skill_categories.items():
                for keyword in keywords:
                    if keyword in skill_lower or skill_lower in keyword:
                        categorized[category].append(skill)
                        categorized_flag = True
                        break
                if categorized_flag:
                    break

            if not categorized_flag:
                uncategorized.append(skill)

        if uncategorized:
            categorized['Other Skills'] = uncategorized

        # Remove empty categories
        categorized = {k: v for k, v in categorized.items() if v}

        return categorized

    def _classify_experience_level(self, years: float) -> str:
        """Classify experience into levels"""
        if years < 1:
            return "Fresher (< 1 year)"
        elif years < 3:
            return "Entry Level (1-3 years)"
        elif years < 5:
            return "Mid Level (3-5 years)"
        elif years < 10:
            return "Senior Level (5-10 years)"
        else:
            return "Expert Level (10+ years)"

    def _generate_profile_summary(self, resume: Resume) -> str:
        """Generate a brief profile summary"""
        parts = []

        if resume.name:
            parts.append(resume.name)

        exp_level = self._classify_experience_level(resume.total_experience_years)
        parts.append(exp_level)

        if resume.skills and len(resume.skills) >= 3:
            top_skills = resume.skills[:3]
            parts.append(f"skilled in {', '.join(top_skills)}")

        if resume.education and len(resume.education) > 0:
            highest_edu = resume.education[0]
            if highest_edu.degree:
                parts.append(f"with {highest_edu.degree}")

        return ' | '.join(parts) if parts else "Profile summary not available"

    def _find_common_gaps(self, valid_resumes: List[Tuple[int, Resume]],
                         match_results: Dict[int, Dict]) -> List[Tuple[str, int]]:
        """Find skills commonly missing across candidates"""
        all_missing_skills = []

        for idx, resume in valid_resumes:
            if idx in match_results:
                missing = match_results[idx].get('missing_required_skills', [])
                all_missing_skills.extend([s.lower() for s in missing])

        skill_gap_frequency = {}
        for skill in all_missing_skills:
            skill_gap_frequency[skill] = skill_gap_frequency.get(skill, 0) + 1

        # Sort by frequency
        common_gaps = sorted(skill_gap_frequency.items(), key=lambda x: x[1], reverse=True)

        return common_gaps

    def generate_comparison_matrix(self, resumes: List[Resume],
                                   match_results: Dict[int, Dict]) -> List[Dict]:
        """
        Generate a comparison matrix for all candidates

        Returns:
            List of dicts with candidate comparison data
        """
        comparison_data = []

        for idx, resume in enumerate(resumes):
            if resume is None:
                continue

            match_result = match_results.get(idx, {})

            comparison_data.append({
                'index': idx,
                'name': resume.name or f"Candidate {idx + 1}",
                'email': resume.email or 'N/A',
                'experience': resume.total_experience_years,
                'skills_count': len(resume.skills) if resume.skills else 0,
                'overall_score': match_result.get('overall_score', 0),
                'skill_score': match_result.get('skill_score', 0),
                'experience_score': match_result.get('experience_score', 0),
                'education_score': match_result.get('education_score', 0),
                'decision': match_result.get('decision', 'N/A'),
                'certifications': len(resume.certifications) if resume.certifications else 0
            })

        # Sort by overall score descending
        comparison_data.sort(key=lambda x: x['overall_score'], reverse=True)

        return comparison_data
