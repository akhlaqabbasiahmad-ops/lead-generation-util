"""
Email Marketing Module
Handles email sending, campaigns, and templates for lead outreach
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Optional
from datetime import datetime
import json
import time


class EmailMarketing:
    """Email marketing functionality for sending emails to leads"""
    
    def __init__(self, smtp_server: str = None, smtp_port: int = None, 
                 smtp_username: str = None, smtp_password: str = None,
                 from_email: str = None, from_name: str = None):
        """
        Initialize email marketing with SMTP configuration.
        
        Args:
            smtp_server: SMTP server address (e.g., smtp.gmail.com)
            smtp_port: SMTP port (587 for TLS, 465 for SSL, 25 for plain)
            smtp_username: SMTP username/email
            smtp_password: SMTP password or app password
            from_email: Sender email address
            from_name: Sender display name
        """
        # Load from environment variables if not provided
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = smtp_username or os.getenv('SMTP_USERNAME', '')
        self.smtp_password = smtp_password or os.getenv('SMTP_PASSWORD', '')
        self.from_email = from_email or os.getenv('FROM_EMAIL', self.smtp_username)
        self.from_name = from_name or os.getenv('FROM_NAME', 'Google Business Scraper')
        
        # Email sending settings
        self.delay_between_emails = float(os.getenv('EMAIL_DELAY', '2.0'))  # seconds
        self.max_emails_per_batch = int(os.getenv('MAX_EMAILS_PER_BATCH', '50'))
        
    def test_connection(self) -> Dict[str, any]:
        """
        Test SMTP connection.
        
        Returns:
            Dictionary with connection status and message
        """
        import socket
        
        try:
            # First, test if we can resolve the hostname
            try:
                socket.gethostbyname(self.smtp_server)
            except socket.gaierror:
                return {
                    'success': False,
                    'message': f'Cannot resolve hostname: {self.smtp_server}',
                    'help': 'Check if the SMTP server address is correct and DNS is working.'
                }
            
            # Test if port is reachable
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                result = sock.connect_ex((self.smtp_server, self.smtp_port))
                sock.close()
                
                if result != 0:
                    return {
                        'success': False,
                        'message': f'Cannot connect to {self.smtp_server}:{self.smtp_port}',
                        'help': (
                            f"Port {self.smtp_port} is not reachable. This usually means:\n"
                            "1. AWS Security Group is blocking outbound SMTP ports\n"
                            "2. Network ACLs are blocking outbound traffic\n"
                            "3. Windows Firewall is blocking outbound connections\n"
                            "4. The SMTP server may be blocking EC2 IP addresses\n\n"
                            "Solutions:\n"
                            "- Allow outbound ports 587, 465, 25 in AWS Security Group\n"
                            "- Run fix_ec2_smtp.bat on the EC2 instance\n"
                            "- Consider using AWS SES (Simple Email Service) instead\n"
                            "- Try a different SMTP provider that allows EC2 connections"
                        )
                    }
            except Exception as port_error:
                return {
                    'success': False,
                    'message': f'Port test failed: {str(port_error)}',
                    'help': 'Network connectivity issue. Check AWS Security Group and Windows Firewall.'
                }
            
            # Now try SMTP connection
            connection_timeout = 30  # 30 seconds
            
            if self.smtp_port == 465:
                # SSL connection
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=connection_timeout)
            else:
                # TLS connection
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=connection_timeout)
                server.starttls()
            
            server.login(self.smtp_username, self.smtp_password)
            server.quit()
            
            return {
                'success': True,
                'message': 'SMTP connection successful'
            }
        except socket.timeout:
            return {
                'success': False,
                'message': 'Connection timeout - server did not respond',
                'help': (
                    "Connection timed out. Possible causes:\n"
                    "1. AWS Security Group blocking outbound SMTP (ports 587/465/25)\n"
                    "2. Network ACLs blocking outbound traffic\n"
                    "3. Windows Firewall blocking connections\n"
                    "4. SMTP provider blocking EC2 IP addresses\n\n"
                    "Quick Fix:\n"
                    "1. AWS Console → EC2 → Security Groups → Your SG → Outbound Rules\n"
                    "   Add: Custom TCP, Port 587, Destination 0.0.0.0/0\n"
                    "2. Run fix_ec2_smtp.bat on EC2 instance (as Administrator)\n"
                    "3. Consider using AWS SES instead of Gmail/Outlook"
                )
            }
        except Exception as e:
            error_msg = str(e)
            
            # Provide helpful error messages for common issues
            if '10060' in error_msg or 'timed out' in error_msg.lower() or 'timeout' in error_msg.lower():
                help_msg = (
                    "Connection timeout (WinError 10060). This means:\n"
                    "1. AWS Security Group is blocking outbound SMTP ports\n"
                    "2. Network ACLs are blocking outbound traffic\n"
                    "3. Windows Firewall is blocking outbound connections\n"
                    "4. SMTP provider may be blocking EC2 IP addresses\n\n"
                    "SOLUTION - Do BOTH:\n"
                    "A. AWS Security Group:\n"
                    "   - Go to EC2 → Security Groups → Your SG\n"
                    "   - Outbound Rules → Edit → Add Rule\n"
                    "   - Type: Custom TCP, Port: 587, Destination: 0.0.0.0/0\n"
                    "   - Save rules\n\n"
                    "B. Windows Firewall (on EC2):\n"
                    "   - Run fix_ec2_smtp.bat as Administrator\n"
                    "   - Or manually allow ports 587, 465, 25\n\n"
                    "ALTERNATIVE: Use AWS SES (Simple Email Service)\n"
                    "   - Works natively on EC2\n"
                    "   - No firewall issues\n"
                    "   - Better deliverability"
                )
                return {
                    'success': False,
                    'message': f'SMTP connection failed: {error_msg}',
                    'help': help_msg
                }
            else:
                return {
                    'success': False,
                    'message': f'SMTP connection failed: {error_msg}'
                }
    
    def send_email(self, to_email: str, subject: str, body_html: str, 
                   body_text: str = None, attachments: List[str] = None,
                   reply_to: str = None) -> Dict[str, any]:
        """
        Send a single email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body_html: HTML email body
            body_text: Plain text email body (optional)
            attachments: List of file paths to attach
            reply_to: Reply-to email address
            
        Returns:
            Dictionary with send status
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if reply_to:
                msg['Reply-To'] = reply_to
            
            # Add text and HTML parts
            if body_text:
                text_part = MIMEText(body_text, 'plain')
                msg.attach(text_part)
            
            html_part = MIMEText(body_html, 'html')
            msg.attach(html_part)
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(file_path)}'
                            )
                            msg.attach(part)
            
            # Send email (increased timeout for EC2/network issues)
            connection_timeout = 60  # 60 seconds for sending
            
            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=connection_timeout)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=connection_timeout)
                server.starttls()
            
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            return {
                'success': True,
                'message': f'Email sent successfully to {to_email}',
                'to': to_email,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to send email to {to_email}: {str(e)}',
                'to': to_email,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def send_bulk_emails(self, recipients: List[Dict[str, str]], 
                        subject_template: str, body_html_template: str,
                        body_text_template: str = None,
                        personalization_fields: Dict[str, str] = None) -> Dict[str, any]:
        """
        Send bulk emails to multiple recipients with personalization.
        
        Args:
            recipients: List of dictionaries with recipient info (email, name, etc.)
            subject_template: Email subject template (use {field_name} for personalization)
            body_html_template: HTML body template
            body_text_template: Plain text body template (optional)
            personalization_fields: Dictionary mapping template fields to recipient fields
            
        Returns:
            Dictionary with bulk send results
        """
        results = {
            'total': len(recipients),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        personalization_fields = personalization_fields or {
            'name': 'name',
            'company': 'name',
            'email': 'email',
            'phone': 'phone',
            'address': 'address',
            'website': 'website'
        }
        
        for i, recipient in enumerate(recipients):
            try:
                # Personalize subject
                subject = subject_template
                for field, recipient_field in personalization_fields.items():
                    value = recipient.get(recipient_field, '')
                    subject = subject.replace(f'{{{field}}}', str(value))
                
                # Personalize HTML body
                body_html = body_html_template
                for field, recipient_field in personalization_fields.items():
                    value = recipient.get(recipient_field, '')
                    body_html = body_html.replace(f'{{{field}}}', str(value))
                
                # Personalize text body
                body_text = None
                if body_text_template:
                    body_text = body_text_template
                    for field, recipient_field in personalization_fields.items():
                        value = recipient.get(recipient_field, '')
                        body_text = body_text.replace(f'{{{field}}}', str(value))
                
                # Send email
                result = self.send_email(
                    to_email=recipient.get('email', ''),
                    subject=subject,
                    body_html=body_html,
                    body_text=body_text
                )
                
                results['details'].append(result)
                
                if result['success']:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                
                # Delay between emails to avoid rate limiting
                if i < len(recipients) - 1:  # Don't delay after last email
                    time.sleep(self.delay_between_emails)
                
                # Batch limit check
                if (i + 1) % self.max_emails_per_batch == 0:
                    print(f"Sent {i + 1} emails, pausing for 60 seconds...")
                    time.sleep(60)  # Longer pause between batches
                    
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'success': False,
                    'message': f'Error processing recipient: {str(e)}',
                    'to': recipient.get('email', 'Unknown'),
                    'error': str(e)
                })
        
        return results
    
    def send_to_leads(self, leads: List[Dict], subject_template: str,
                     body_html_template: str, body_text_template: str = None,
                     filter_condition: callable = None) -> Dict[str, any]:
        """
        Send emails to scraped leads.
        
        Args:
            leads: List of lead dictionaries from scraper
            subject_template: Email subject template
            body_html_template: HTML body template
            body_text_template: Plain text body template (optional)
            filter_condition: Optional function to filter leads (returns True to include)
            
        Returns:
            Dictionary with send results
        """
        # Filter leads that have email addresses
        recipients = []
        for lead in leads:
            email = lead.get('email') or lead.get('Email')
            if email and email != 'N/A' and '@' in email:
                # Apply custom filter if provided
                if filter_condition is None or filter_condition(lead):
                    recipients.append({
                        'email': email,
                        'name': lead.get('name') or lead.get('Company Name') or 'Business Owner',
                        'company': lead.get('name') or lead.get('Company Name') or '',
                        'phone': lead.get('phone') or lead.get('Phone') or '',
                        'address': lead.get('address') or lead.get('Address') or '',
                        'website': lead.get('website') or lead.get('Website') or '',
                        'lead_score': lead.get('lead_score') or lead.get('Lead Score') or 0
                    })
        
        if not recipients:
            return {
                'success': False,
                'message': 'No valid email addresses found in leads',
                'total': 0,
                'successful': 0,
                'failed': 0
            }
        
        return self.send_bulk_emails(
            recipients=recipients,
            subject_template=subject_template,
            body_html_template=body_html_template,
            body_text_template=body_text_template
        )


class EmailTemplates:
    """Pre-built email templates for lead outreach"""
    
    @staticmethod
    def get_template(template_name: str) -> Dict[str, str]:
        """
        Get email template by name.
        
        Args:
            template_name: Name of template ('intro', 'followup', 'partnership', etc.)
            
        Returns:
            Dictionary with 'subject', 'html', and 'text' keys
        """
        templates = {
            'intro': {
                'subject': 'Introduction: {company} - Partnership Opportunity',
                'html': '''
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #667eea;">Hello {name},</h2>
                        <p>I hope this email finds you well. I came across <strong>{company}</strong> and was impressed by your business.</p>
                        <p>I wanted to reach out to explore potential partnership opportunities that could benefit both our organizations.</p>
                        <p>Would you be available for a brief call this week to discuss how we might work together?</p>
                        <p>Best regards,<br>{sender_name}</p>
                    </div>
                </body>
                </html>
                ''',
                'text': '''
Hello {name},

I hope this email finds you well. I came across {company} and was impressed by your business.

I wanted to reach out to explore potential partnership opportunities that could benefit both our organizations.

Would you be available for a brief call this week to discuss how we might work together?

Best regards,
{sender_name}
                '''
            },
            'followup': {
                'subject': 'Following up: {company}',
                'html': '''
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #667eea;">Hi {name},</h2>
                        <p>I wanted to follow up on my previous message regarding potential collaboration with <strong>{company}</strong>.</p>
                        <p>I understand you're busy, but I believe there's a great opportunity for us to work together.</p>
                        <p>Please let me know if you'd like to schedule a quick call or if you have any questions.</p>
                        <p>Looking forward to hearing from you.</p>
                        <p>Best regards,<br>{sender_name}</p>
                    </div>
                </body>
                </html>
                ''',
                'text': '''
Hi {name},

I wanted to follow up on my previous message regarding potential collaboration with {company}.

I understand you're busy, but I believe there's a great opportunity for us to work together.

Please let me know if you'd like to schedule a quick call or if you have any questions.

Looking forward to hearing from you.

Best regards,
{sender_name}
                '''
            },
            'partnership': {
                'subject': 'Partnership Opportunity for {company}',
                'html': '''
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #667eea;">Dear {name},</h2>
                        <p>I'm reaching out to <strong>{company}</strong> because I believe we have complementary services that could create value for both our businesses.</p>
                        <p>I'd love to explore how we might partner together to:</p>
                        <ul>
                            <li>Expand our respective customer bases</li>
                            <li>Offer combined solutions</li>
                            <li>Create mutual growth opportunities</li>
                        </ul>
                        <p>Would you be open to a 15-minute conversation to discuss this further?</p>
                        <p>Best regards,<br>{sender_name}</p>
                    </div>
                </body>
                </html>
                ''',
                'text': '''
Dear {name},

I'm reaching out to {company} because I believe we have complementary services that could create value for both our businesses.

I'd love to explore how we might partner together to expand our respective customer bases, offer combined solutions, and create mutual growth opportunities.

Would you be open to a 15-minute conversation to discuss this further?

Best regards,
{sender_name}
                '''
            },
            'custom': {
                'subject': 'Custom Subject',
                'html': '<html><body><p>Custom HTML email body</p></body></html>',
                'text': 'Custom plain text email body'
            }
        }
        
        return templates.get(template_name, templates['custom'])

