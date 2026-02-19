"""Email utility for sending reports"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict
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
                                  to_email: str,
                                  candidate_name: str,
                                  report_content: str,
                                  sender_email: Optional[str] = None,
                                  sender_password: Optional[str] = None) -> Dict:
        """
        Send gap analysis report via email
        
        Args:
            to_email: Recipient email address
            candidate_name: Name of the candidate
            report_content: Text content of the gap analysis report
            sender_email: Sender's email (default from env var)
            sender_password: Sender's password or app password (default from env var)
            
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
        
        # Validate recipient email
        if not to_email or '@' not in to_email:
            return {
                'success': False,
                'message': 'Invalid recipient email address'
            }
        
        # Create message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = to_email
        message['Subject'] = f"Career Development: Gap Analysis Report for {candidate_name or 'You'}"
        
        # Email body
        email_body = f"""
Dear {candidate_name or 'Candidate'},

Thank you for your interest in improving your professional profile!

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
            server.send_message(message)
            server.quit()
            
            return {
                'success': True,
                'message': f'Gap analysis report successfully sent to {to_email}'
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
