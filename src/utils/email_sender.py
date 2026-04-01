"""Email utility for sending reports"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, Dict, List, Union
import mimetypes
import os
import socket


class EmailSender:
    """Send emails with gap analysis reports"""
    
    def __init__(self, smtp_server: str = "smtp.gmail.com", 
                 smtp_port: int = 587,
                 use_ssl: bool = False,
                 timeout: int = 30):
        """
        Initialize email sender
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port (587 for TLS, 465 for SSL)
            use_ssl: Use SSL instead of TLS (for port 465)
            timeout: Connection timeout in seconds
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.use_ssl = use_ssl
        self.timeout = timeout
        
    def send_gap_analysis_report(self,
                                  to_email: Union[str, List[str]],
                                  candidate_name: str,
                                  report_content: str,
                                  sender_email: Optional[str] = None,
                                  sender_password: Optional[str] = None,
                                  cc_email: Optional[Union[str, List[str]]] = None) -> Dict:
        """
        Send gap analysis report via email
        
        Args:
            to_email: Recipient email address(es) — a single address or a list of addresses
            candidate_name: Name of the candidate
            report_content: Text content of the gap analysis report
            sender_email: Sender's email (default from env var)
            sender_password: Sender's password or app password (default from env var)
            cc_email: Optional CC recipient email address(es)
            
        Returns:
            Dict with success status and message
        """
        # Get credentials from environment variables if not provided
        if not sender_email:
            sender_email = os.getenv('SENDER_EMAIL')
        if not sender_password:
            sender_password = os.getenv('SENDER_PASSWORD')
        
        if not sender_email or not sender_password:
            return {
                'success': False,
                'message': 'Email credentials not configured. Please set SENDER_EMAIL and SENDER_PASSWORD environment variables.'
            }
        
        # Normalise to_email to a list
        if isinstance(to_email, str):
            to_list = [addr.strip() for addr in to_email.split(',') if addr.strip()]
        else:
            to_list = [addr.strip() for addr in to_email if addr.strip()]

        # Normalise cc_email to a list
        if cc_email is None:
            cc_list = []
        elif isinstance(cc_email, str):
            cc_list = [addr.strip() for addr in cc_email.split(',') if addr.strip()]
        else:
            cc_list = [addr.strip() for addr in cc_email if addr.strip()]

        # Validate all recipient addresses
        invalid = [addr for addr in to_list + cc_list if '@' not in addr]
        if not to_list:
            return {
                'success': False,
                'message': 'At least one valid recipient email address is required'
            }
        if invalid:
            return {
                'success': False,
                'message': f'Invalid email address(es): {", ".join(invalid)}'
            }

        # Create message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = ', '.join(to_list)
        if cc_list:
            message['Cc'] = ', '.join(cc_list)
        message['Subject'] = f"Career Development: Gap Analysis Report for {candidate_name or 'You'}"
        
        # Email body
        email_body = f"""
Dear {candidate_name or 'Candidate'},

Please find below your personalized Gap Analysis Report. This report highlights areas where you can focus your efforts to better align with job market requirements and enhance your career prospects.

{'=' * 80}

{report_content}

{'=' * 80}

We recommend reviewing this analysis carefully and taking action on the suggested improvement areas. Focus on the priority skills and certifications that will have the most impact on your career growth.

Best regards,
AI Resume Screening System
Career Development Team

---
This is an automated message. Please do not reply to this email.
"""
        
        # Attach the message body
        message.attach(MIMEText(email_body, 'plain'))

        # Create SMTP session with timeout and SSL/TLS support
        try:
            if self.use_ssl:
                # Use SMTP_SSL for port 465
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=self.timeout)
            else:
                # Use SMTP with STARTTLS for port 587
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.timeout)
                server.starttls()  # Enable security
            
            server.login(sender_email, sender_password)
            all_recipients = to_list + cc_list
            server.send_message(message, to_addrs=all_recipients)
            server.quit()

            to_display = ', '.join(to_list)
            cc_display = f' (CC: {", ".join(cc_list)})' if cc_list else ''
            return {
                'success': True,
                'message': f'Gap analysis report successfully sent to {to_display}{cc_display}'
            }
            
        except socket.timeout:
            return {
                'success': False,
                'message': f'Connection timeout. Unable to reach {self.smtp_server}:{self.smtp_port}. This may be due to firewall/antivirus blocking or network restrictions. Try port 465 with SSL, or check your firewall settings.'
            }
        except socket.error as e:
            if hasattr(e, 'errno') and e.errno == 10060:
                return {
                    'success': False,
                    'message': f'Connection failed (WinError 10060). The SMTP server is not reachable. Possible causes:\n• Firewall or antivirus blocking port {self.smtp_port}\n• ISP blocking SMTP connections\n• Network restrictions\n\nSuggestions:\n• Try using port 465 with SSL instead\n• Check Windows Firewall settings\n• Temporarily disable antivirus to test\n• Try a different network'
                }
            return {
                'success': False,
                'message': f'Network error: {str(e)}'
            }
        except smtplib.SMTPAuthenticationError:
            return {
                'success': False,
                'message': 'Email authentication failed. Please check your credentials. For Gmail, use an App Password instead of your regular password.'
            }
        except smtplib.SMTPException as e:
            return {
                'success': False,
                'message': f'SMTP error occurred: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error sending email: {str(e)}'
            }

    # ------------------------------------------------------------------
    # Shortlist / Rejection emails
    # ------------------------------------------------------------------

    def send_shortlist_email(self,
                             to_email: Union[str, List[str]],
                             candidate_name: str,
                             company_name: str,
                             job_title: str,
                             sender_email: Optional[str] = None,
                             sender_password: Optional[str] = None,
                             cc_email: Optional[Union[str, List[str]]] = None) -> Dict:
        """Send an interview-availability confirmation email to a shortlisted candidate."""
        if not sender_email:
            sender_email = os.getenv('SENDER_EMAIL')
        if not sender_password:
            sender_password = os.getenv('SENDER_PASSWORD')
        if not sender_email or not sender_password:
            return {'success': False,
                    'message': 'Email credentials not configured.'}

        if isinstance(to_email, str):
            to_list = [a.strip() for a in to_email.split(',') if a.strip()]
        else:
            to_list = [a.strip() for a in to_email if a.strip()]
        if isinstance(cc_email, str):
            cc_list = [a.strip() for a in cc_email.split(',') if a.strip()]
        elif cc_email:
            cc_list = list(cc_email)
        else:
            cc_list = []

        if not to_list:
            return {'success': False, 'message': 'No valid recipient addresses.'}

        subject = f"Interview Availability Confirmation for {company_name}"
        body = (
            f"Dear {candidate_name},\n\n"
            f"We are pleased to inform you that your profile has been shortlisted for the "
            f"{job_title} position at {company_name}.\n\n"
            f"We would like to know your availability and interest in proceeding with the "
            f"interview process. If you are interested, kindly reply to this email with your "
            f"consent, and we will coordinate with you to schedule an interview session at a "
            f"mutually convenient time.\n\n"
            f"We look forward to your response.\n\n"
            f"Best regards,\n"
            f"Talent Acquisition Team\n"
            f"{company_name}\n\n"
            f"---\n"
            f"This is an automated notification. Please reply directly to this email to confirm\n"
            f"your interest."
        )
        return self._send(to_list, cc_list, subject, body, sender_email, sender_password)

    def send_rejection_email(self,
                             to_email: Union[str, List[str]],
                             candidate_name: str,
                             company_name: str,
                             job_title: str,
                             gap_report: str,
                             sender_email: Optional[str] = None,
                             sender_password: Optional[str] = None,
                             cc_email: Optional[Union[str, List[str]]] = None) -> Dict:
        """Send a professional rejection email with the gap analysis report attached inline."""
        if not sender_email:
            sender_email = os.getenv('SENDER_EMAIL')
        if not sender_password:
            sender_password = os.getenv('SENDER_PASSWORD')
        if not sender_email or not sender_password:
            return {'success': False,
                    'message': 'Email credentials not configured.'}

        if isinstance(to_email, str):
            to_list = [a.strip() for a in to_email.split(',') if a.strip()]
        else:
            to_list = [a.strip() for a in to_email if a.strip()]
        if isinstance(cc_email, str):
            cc_list = [a.strip() for a in cc_email.split(',') if a.strip()]
        elif cc_email:
            cc_list = list(cc_email)
        else:
            cc_list = []

        if not to_list:
            return {'success': False, 'message': 'No valid recipient addresses.'}

        subject = f"Application Update – {job_title} at {company_name}"
        separator = "=" * 70
        body = (
            f"Dear {candidate_name},\n\n"
            f"Thank you for your interest in the {job_title} position at {company_name} "
            f"and for taking the time to apply.\n\n"
            f"After careful consideration, we regret to inform you that your application has "
            f"not been shortlisted for further stages of the selection process. While your "
            f"qualifications are commendable, we have decided to move forward with candidates "
            f"whose profiles more closely match our current requirements.\n\n"
            f"We truly appreciate your interest in joining our organisation and encourage you "
            f"to apply for future opportunities that align with your experience and skills.\n\n"
            f"Please find below your personalised Gap Analysis Report. This report highlights "
            f"areas where you can focus your efforts to better align with job market requirements "
            f"and enhance your career prospects.\n\n"
            f"{separator}\n"
            f"GAP ANALYSIS REPORT\n"
            f"{separator}\n\n"
            f"{gap_report}\n\n"
            f"{separator}\n\n"
            f"Wishing you all the best in your job search.\n\n"
            f"Best regards,\n"
            f"Talent Acquisition Team\n"
            f"{company_name}\n\n"
            f"---\n"
            f"This is an automated notification."
        )
        return self._send(to_list, cc_list, subject, body, sender_email, sender_password)

    def send_review_email(self,
                         to_email: Union[str, List[str]],
                         candidate_name: str,
                         company_name: str,
                         job_title: str,
                         overall_score: float,
                         sender_email: Optional[str] = None,
                         sender_password: Optional[str] = None,
                         cc_email: Optional[Union[str, List[str]]] = None,
                         resume_bytes: Optional[bytes] = None,
                         resume_filename: Optional[str] = None,
                         match_summary: Optional[str] = None) -> Dict:
        """Send a manual-review request to the hiring manager, with resume attached."""
        if not sender_email:
            sender_email = os.getenv('SENDER_EMAIL')
        if not sender_password:
            sender_password = os.getenv('SENDER_PASSWORD')
        if not sender_email or not sender_password:
            return {'success': False, 'message': 'Email credentials not configured.'}

        if isinstance(to_email, str):
            to_list = [a.strip() for a in to_email.split(',') if a.strip()]
        else:
            to_list = [a.strip() for a in to_email if a.strip()]
        if isinstance(cc_email, str):
            cc_list = [a.strip() for a in cc_email.split(',') if a.strip()]
        elif cc_email:
            cc_list = list(cc_email)
        else:
            cc_list = []

        if not to_list:
            return {'success': False, 'message': 'No valid recipient addresses.'}

        subject = f"[Review Required] {candidate_name} \u2013 {job_title} at {company_name}"
        attachment_note = (
            f"The candidate's resume is attached for your reference."
            if resume_bytes else
            "Please access the candidate profile in the system for the full resume."
        )
        summary_section = f"\n\nMatch Summary:\n{match_summary}" if match_summary else ""
        body = (
            f"Dear Hiring Manager,\n\n"
            f"A candidate profile for the {job_title} position at {company_name} has been "
            f"flagged for manual review by the AI Screening System.\n\n"
            f"Candidate   : {candidate_name}\n"
            f"Role Applied: {job_title}\n"
            f"Company     : {company_name}\n"
            f"AI Match Score: {overall_score:.1f}%"
            f"{summary_section}\n\n"
            f"The candidate\u2019s overall score falls within the review range (60\u201375%), "
            f"indicating a moderate fit that warrants human judgement before a final "
            f"decision is made.\n\n"
            f"{attachment_note}\n\n"
            f"Please review the application and advise on the next steps at your earliest "
            f"convenience.\n\n"
            f"Best regards,\n"
            f"AI Resume Screening System\n"
            f"{company_name}\n\n"
            f"---\n"
            f"This is an automated notification. Please do not reply to this email."
        )

        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = ', '.join(to_list)
        if cc_list:
            message['Cc'] = ', '.join(cc_list)
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        if resume_bytes and resume_filename:
            mime_type, _ = mimetypes.guess_type(resume_filename)
            maintype, subtype = (mime_type or 'application/octet-stream').split('/', 1)
            part = MIMEBase(maintype, subtype)
            part.set_payload(resume_bytes)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename=resume_filename)
            message.attach(part)

        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=self.timeout)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.timeout)
                server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message, to_addrs=to_list + cc_list)
            server.quit()
            to_display = ', '.join(to_list)
            cc_display = f' (CC: {", ".join(cc_list)})' if cc_list else ''
            attach_note = ' (with resume attached)' if resume_bytes else ''
            return {'success': True,
                    'message': f'Review request sent to {to_display}{cc_display}{attach_note}'}
        except socket.timeout:
            return {'success': False,
                    'message': f'Connection timeout reaching {self.smtp_server}:{self.smtp_port}.'}
        except socket.error as e:
            return {'success': False, 'message': f'Network error: {e}'}
        except smtplib.SMTPAuthenticationError:
            return {'success': False,
                    'message': 'Authentication failed. For Gmail use an App Password.'}
        except smtplib.SMTPException as e:
            return {'success': False, 'message': f'SMTP error: {e}'}
        except Exception as e:
            return {'success': False, 'message': f'Error sending email: {e}'}

    # ------------------------------------------------------------------
    # Shared send helper
    # ------------------------------------------------------------------

    def _send(self, to_list: List[str], cc_list: List[str],
              subject: str, body: str,
              sender_email: str, sender_password: str) -> Dict:
        """Internal method: build message and send via SMTP."""
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = ', '.join(to_list)
        if cc_list:
            message['Cc'] = ', '.join(cc_list)
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port,
                                          timeout=self.timeout)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port,
                                      timeout=self.timeout)
                server.starttls()

            server.login(sender_email, sender_password)
            server.send_message(message, to_addrs=to_list + cc_list)
            server.quit()

            to_display = ', '.join(to_list)
            cc_display = f' (CC: {", ".join(cc_list)})' if cc_list else ''
            return {'success': True,
                    'message': f'Email sent to {to_display}{cc_display}'}

        except socket.timeout:
            return {'success': False,
                    'message': (f'Connection timeout reaching '
                                f'{self.smtp_server}:{self.smtp_port}.')}
        except socket.error as e:
            return {'success': False, 'message': f'Network error: {e}'}
        except smtplib.SMTPAuthenticationError:
            return {'success': False,
                    'message': ('Authentication failed. For Gmail use an App Password.')}
        except smtplib.SMTPException as e:
            return {'success': False, 'message': f'SMTP error: {e}'}
        except Exception as e:
            return {'success': False, 'message': f'Error sending email: {e}'}

    def test_connection(self, sender_email: str, sender_password: str) -> Dict:
        """
        Test SMTP connection and credentials

        Args:
            sender_email: Sender's email
            sender_password: Sender's password
            
        Returns:
            Dict with success status and detailed message
        """
        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=self.timeout)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.timeout)
                server.starttls()
            
            server.login(sender_email, sender_password)
            server.quit()
            
            return {
                'success': True,
                'message': f'Successfully connected to {self.smtp_server}:{self.smtp_port}'
            }
        except socket.timeout:
            return {
                'success': False,
                'message': f'Connection timeout to {self.smtp_server}:{self.smtp_port}'
            }
        except socket.error as e:
            return {
                'success': False,
                'message': f'Connection error: {str(e)}'
            }
        except smtplib.SMTPAuthenticationError:
            return {
                'success': False,
                'message': 'Authentication failed. Check credentials or use App Password for Gmail.'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Connection test failed: {str(e)}'
            }
