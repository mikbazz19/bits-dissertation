"""Report generation for screening results"""

from typing import Dict, List, Optional
from datetime import datetime
from io import BytesIO
from ..models.resume import Resume
from ..models.job import JobDescription

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class ReportGenerator:
    """Generate detailed screening reports"""
    
    def generate_screening_report(self, 
                                  resume: Resume, 
                                  job: JobDescription,
                                  match_result: Dict,
                                  gap_analysis: Dict) -> str:
        """Generate comprehensive screening report"""
        
        report = []
        report.append("=" * 80)
        report.append("CANDIDATE SCREENING REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Candidate Information
        report.append("CANDIDATE INFORMATION")
        report.append("-" * 80)
        report.append(f"Name: {resume.name or 'N/A'}")
        report.append(f"Email: {resume.email or 'N/A'}")
        report.append(f"Phone: {resume.phone or 'N/A'}")
        report.append(f"Total Experience: {resume.total_experience_years} years")
        report.append("")
        
        # Job Information
        report.append("JOB DETAILS")
        report.append("-" * 80)
        report.append(f"Title: {job.title}")
        report.append(f"Company: {job.company}")
        report.append(f"Required Experience: {job.required_experience} years")
        report.append("")
        
        # Match Summary
        report.append("MATCH SUMMARY")
        report.append("-" * 80)
        report.append(f"Overall Match Score: {match_result['overall_score']}%")
        report.append(f"Match Level: {match_result['match_level']}")
        report.append(f"Skills Match: {match_result['skill_score']}%")
        report.append(f"Experience Match: {match_result['experience_score']}%")
        report.append(f"Education Match: {match_result['education_score']}%")
        report.append("")
        
        # Matched Skills
        if match_result.get('matched_skills'):
            report.append("MATCHED SKILLS")
            report.append("-" * 80)
            for skill in match_result['matched_skills']:
                report.append(f"  ✓ {skill}")
            report.append("")
        
        # Skill Gaps
        report.append("SKILL GAP ANALYSIS")
        report.append("-" * 80)
        
        if match_result.get('missing_required_skills'):
            report.append("Missing Required Skills:")
            for skill in match_result['missing_required_skills']:
                report.append(f"  ✗ {skill}")
        else:
            report.append("  ✓ All required skills present")
        
        report.append("")
        
        if match_result.get('missing_preferred_skills'):
            report.append("Missing Preferred Skills:")
            for skill in match_result['missing_preferred_skills']:
                report.append(f"  • {skill}")
        report.append("")
        
        # Experience Analysis
        exp_gaps = gap_analysis.get('experience_gaps', {})
        report.append("EXPERIENCE ANALYSIS")
        report.append("-" * 80)
        report.append(f"Required: {exp_gaps.get('required_experience', 0)} years")
        report.append(f"Candidate: {exp_gaps.get('candidate_experience', 0)} years")
        if exp_gaps.get('meets_requirement'):
            report.append("  ✓ Meets experience requirement")
        else:
            report.append(f"  ✗ Gap: {exp_gaps.get('experience_gap_years', 0)} years")
        report.append("")
        
        # Improvement Suggestions
        suggestions = gap_analysis.get('improvement_suggestions', [])
        if suggestions:
            report.append("IMPROVEMENT RECOMMENDATIONS")
            report.append("-" * 80)
            for i, suggestion in enumerate(suggestions, 1):
                report.append(f"{i}. {suggestion}")
            report.append("")
        
        # Final Recommendation
        report.append("RECOMMENDATION")
        report.append("-" * 80)
        report.append(match_result.get('recommendation', 'Further review recommended'))
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def generate_gap_report(self, gap_analysis: Dict, match_result: Optional[Dict] = None) -> str:
        """Generate detailed gap analysis report"""
        
        report = []
        report.append("")
        
        # Skill Gaps
        skill_gaps = gap_analysis.get('skill_gaps', {})
        report.append("SKILLS COVERAGE")
        report.append("-" * 80)

        # Prefer authoritative scores from match_result (JobMatcher) if available
        if match_result:
            report.append(f"Overall Match Score : {match_result.get('overall_score', 0):.1f}%")
            report.append(f"Skills Match        : {match_result.get('skill_score', 0):.1f}%")
            report.append(f"Experience Match    : {match_result.get('experience_score', 0):.1f}%")
            report.append(f"Education Match     : {match_result.get('education_score', 0):.1f}%")
        else:
            report.append(f"Required Skills Coverage: {skill_gaps.get('required_skills_coverage', 0)}%")
            report.append(f"Preferred Skills Coverage: {skill_gaps.get('preferred_skills_coverage', 0)}%")
        report.append("")

        missing_required = skill_gaps.get('missing_required_skills', [])
        missing_preferred = skill_gaps.get('missing_preferred_skills', [])

        if missing_required:
            report.append("Missing Required Skills:")
            for skill in missing_required:
                report.append(f"  ✗ {skill}")
            report.append("")

        if missing_preferred:
            report.append("Missing Preferred Skills:")
            for skill in missing_preferred:
                report.append(f"  ○ {skill}")
            report.append("")
        
        # Priority Areas
        priority = gap_analysis.get('priority_areas', [])
        if priority:
            report.append("PRIORITY IMPROVEMENT AREAS")
            report.append("-" * 80)
            for area in priority:
                report.append(f"  • {area}")
            report.append("")
        
        # Suggestions
        suggestions = gap_analysis.get('improvement_suggestions', [])
        if suggestions:
            report.append("ACTION ITEMS")
            report.append("-" * 80)
            for i, suggestion in enumerate(suggestions, 1):
                report.append(f"{i}. {suggestion}")
            report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def generate_comparison_report(self, candidates: List[Dict]) -> str:
        """Generate comparison report for multiple candidates"""
        
        report = []
        report.append("=" * 80)
        report.append("CANDIDATE COMPARISON REPORT")
        report.append("=" * 80)
        report.append(f"Total Candidates: {len(candidates)}")
        report.append("")
        
        report.append(f"{'Rank':<6} {'Name':<25} {'Overall':<10} {'Skills':<10} {'Experience':<12} {'Match Level':<15}")
        report.append("-" * 80)
        
        for i, candidate in enumerate(candidates, 1):
            resume = candidate.get('resume')
            match = candidate.get('match_result', {})
            
            name = (resume.name or 'Unknown')[:24]
            overall = f"{match.get('overall_score', 0):.1f}%"
            skills = f"{match.get('skill_score', 0):.1f}%"
            exp = f"{match.get('experience_score', 0):.1f}%"
            level = match.get('match_level', 'N/A')[:14]
            
            report.append(f"{i:<6} {name:<25} {overall:<10} {skills:<10} {exp:<12} {level:<15}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def export_to_dict(self, resume: Resume, job: JobDescription, 
                      match_result: Dict, gap_analysis: Dict) -> Dict:
        """Export screening results as structured dictionary"""
        
        return {
            'timestamp': datetime.now().isoformat(),
            'candidate': resume.to_dict(),
            'job': job.to_dict(),
            'match_results': match_result,
            'gap_analysis': gap_analysis
        }

    # ── Evaluation metrics integration ────────────────────────────────────

    def generate_evaluation_report(
        self,
        extraction_metrics: Optional[Dict] = None,
        matching_metrics: Optional[Dict] = None,
    ) -> str:
        """
        Generate a formatted evaluation metrics report.

        Parameters
        ----------
        extraction_metrics : dict from ExtractionMetrics.to_dict()
        matching_metrics   : dict from MatchingMetrics.to_dict()

        If neither is supplied the method runs the evaluators against the
        bundled sample resumes and job descriptions to produce live results.
        """
        # Lazily run evaluators if callers don't supply pre-computed dicts
        if extraction_metrics is None or matching_metrics is None:
            try:
                from ..evaluation.evaluator import ExtractionEvaluator
                from ..evaluation.matching_evaluator import MatchingEvaluator
                from ..evaluation.ground_truth import (
                    ALL_RESUME_ANNOTATIONS,
                    ALL_JOB_ANNOTATIONS,
                    JOB_ANNOTATION_MAP,
                )
                ext_ev  = ExtractionEvaluator()
                mat_ev  = MatchingEvaluator()
                extraction_metrics = ext_ev.evaluate_all(ALL_RESUME_ANNOTATIONS).to_dict()
                matching_metrics   = mat_ev.evaluate(
                    ALL_RESUME_ANNOTATIONS, ALL_JOB_ANNOTATIONS, JOB_ANNOTATION_MAP
                ).to_dict()
            except Exception as e:
                return f"[Evaluation failed: {e}]"

        report = []
        report.append("=" * 80)
        report.append("SYSTEM EVALUATION REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")

        # ── Extraction metrics table ───────────────────────────────────────
        report.append("EXTRACTION MODULE METRICS  (Precision / Recall / F1-Score)")
        report.append("-" * 80)
        report.append(f"{'Module':<30}  {'Precision':>10}  {'Recall':>8}  {'F1-Score':>10}")
        report.append("-" * 80)

        for m in extraction_metrics.get("per_module", []):
            report.append(
                f"{m['module']:<30}  "
                f"{m['precision']:>10.2%}  "
                f"{m['recall']:>8.2%}  "
                f"{m['f1_score']:>10.4f}"
            )

        mp = extraction_metrics.get("macro_precision", 0)
        mr = extraction_metrics.get("macro_recall", 0)
        mf = extraction_metrics.get("macro_f1", 0)
        report.append("-" * 80)
        report.append(f"{'Macro Average':<30}  {mp:>10.2%}  {mr:>8.2%}  {mf:>10.4f}")
        report.append("")

        # ── Matching metrics ───────────────────────────────────────────────
        report.append("MATCHING ENGINE METRICS")
        report.append("-" * 80)
        acc = matching_metrics.get("shortlisting_accuracy", 0)
        mae = matching_metrics.get("mean_absolute_error", 0)
        rho = matching_metrics.get("spearman_rho")
        n   = matching_metrics.get("n_samples", 0)
        report.append(f"Shortlisting Accuracy  : {acc:.2%}  (over {n} candidate-job pairs)")
        report.append(f"Mean Absolute Error    : {mae:.2f} score points")
        report.append(f"Spearman's Rho (ρ)     : {rho if rho is not None else 'N/A (< 2 rank pairs)'}")
        report.append("")
        report.append("=" * 80)

        return "\n".join(report)
    
    def generate_pdf_report(self, resume: Resume, job: JobDescription,
                           match_result: Dict, gap_analysis: Dict) -> BytesIO:
        """Generate PDF screening report"""
        
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required for PDF generation. Install with: pip install reportlab")
        
        # Create a BytesIO buffer
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                               rightMargin=0.75*inch, leftMargin=0.75*inch,
                               topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        elements.append(Paragraph("CANDIDATE SCREENING REPORT", title_style))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Candidate Information
        elements.append(Paragraph("CANDIDATE INFORMATION", heading_style))
        candidate_data = [
            ['Name:', resume.name or 'N/A'],
            ['Email:', resume.email or 'N/A'],
            ['Phone:', resume.phone or 'N/A'],
            ['Total Experience:', f"{resume.total_experience_years} years"]
        ]
        candidate_table = Table(candidate_data, colWidths=[2*inch, 4*inch])
        candidate_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(candidate_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Job Information
        elements.append(Paragraph("JOB DETAILS", heading_style))
        job_data = [
            ['Title:', job.title],
            ['Company:', job.company],
            ['Required Experience:', f"{job.required_experience} years"]
        ]
        job_table = Table(job_data, colWidths=[2*inch, 4*inch])
        job_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(job_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Match Summary
        elements.append(Paragraph("MATCH SUMMARY", heading_style))
        
        # Overall score with color coding
        score = match_result['overall_score']
        score_color = colors.green if score >= 70 else (colors.orange if score >= 50 else colors.red)
        
        match_data = [
            ['Overall Match Score:', f"{score}%", match_result['match_level']],
            ['Skills Match:', f"{match_result['skill_score']}%", ''],
            ['Experience Match:', f"{match_result['experience_score']}%", ''],
            ['Education Match:', f"{match_result['education_score']}%", '']
        ]
        match_table = Table(match_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        match_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(match_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Matched Skills
        if match_result.get('matched_skills'):
            elements.append(Paragraph("MATCHED SKILLS", heading_style))
            skills_text = ", ".join(match_result['matched_skills'][:15])
            elements.append(Paragraph(f"<font color='green'>✓</font> {skills_text}", styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Missing Skills
        if match_result.get('missing_required_skills'):
            elements.append(Paragraph("MISSING REQUIRED SKILLS", heading_style))
            for skill in match_result['missing_required_skills'][:10]:
                elements.append(Paragraph(f"<font color='red'>✗</font> {skill}", styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Gap Analysis
        elements.append(Paragraph("SKILL GAP ANALYSIS", heading_style))
        skill_gaps = gap_analysis.get('skill_gaps', {})
        gap_data = [
            ['Required Skills Coverage:', f"{skill_gaps.get('required_skills_coverage', 0)}%"],
            ['Preferred Skills Coverage:', f"{skill_gaps.get('preferred_skills_coverage', 0)}%"],
            ['Total Missing Skills:', str(skill_gaps.get('total_missing', 0))]
        ]
        gap_table = Table(gap_data, colWidths=[3*inch, 3*inch])
        gap_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(gap_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Experience Gap
        exp_gaps = gap_analysis.get('experience_gaps', {})
        elements.append(Paragraph("EXPERIENCE ANALYSIS", heading_style))
        exp_text = f"Required: {exp_gaps.get('required_experience', 0)} years | "
        exp_text += f"Candidate: {exp_gaps.get('candidate_experience', 0)} years"
        if exp_gaps.get('meets_requirement'):
            exp_text += " <font color='green'>✓ Meets requirement</font>"
        else:
            exp_text += f" <font color='red'>✗ Gap: {exp_gaps.get('experience_gap_years', 0)} years</font>"
        elements.append(Paragraph(exp_text, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Recommendations
        elements.append(Paragraph("IMPROVEMENT RECOMMENDATIONS", heading_style))
        suggestions = gap_analysis.get('improvement_suggestions', [])
        for i, suggestion in enumerate(suggestions[:5], 1):
            elements.append(Paragraph(f"{i}. {suggestion}", styles['Normal']))
            elements.append(Spacer(1, 0.05*inch))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Final Recommendation
        elements.append(Paragraph("FINAL RECOMMENDATION", heading_style))
        recommendation_text = match_result.get('recommendation', 'Further review recommended')
        elements.append(Paragraph(recommendation_text, styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        
        # Get the value from the BytesIO buffer
        buffer.seek(0)
        return buffer
