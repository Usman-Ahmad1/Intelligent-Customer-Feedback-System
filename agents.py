"""
Agents with Email Sending Capability
"""
from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any
from langchain_groq import ChatGroq
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

from config import Config
from logging_config import logger

# ============================================================================
# TEST EMAIL CONFIGURATION
# ============================================================================
# Get test email from .env, fallback to your email
TEST_EMAIL = os.getenv("TEST_CUSTOMER_EMAIL", "uahmaddatascientist@gmail.com")

class AgentState(TypedDict):
    """State for LangGraph agents."""
    feedback: str
    sentiment: str
    response: str
    action_taken: str
    ticket_id: str
    email_sent: bool
    error: str
    customer_email: str  # Add customer email

class FeedbackAgents:
    """LangGraph agents for handling feedback actions with email sending."""
    
    def __init__(self):
        self.llm = ChatGroq(
            model=Config.GROQ_MODEL,
            temperature=0.3,
            api_key=Config.GROQ_API_KEY
        )
        
        # Email configuration from environment
        self.email_username = os.getenv("EMAIL_USERNAME", "uahmaddatascientist@gmail.com")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")  # Need to set this
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.from_email = os.getenv("FROM_EMAIL", "uahmaddatascientist@gmail.com")
        
    def create_positive_agent(self):
        """Create agent for positive feedback handling."""
        
        def send_thank_you_email(state: AgentState) -> AgentState:
            """Send thank you email asking for 5-star review."""
            try:
                # Get customer email - use test email if none provided
                customer_email = state.get('customer_email')
                if not customer_email or customer_email == 'customer@example.com':
                    customer_email = TEST_EMAIL
                    logger.info(f"Using test email: {customer_email}")
                
                # Generate personalized email using LLM
                email_prompt = f"""
                Create a warm, professional thank you email to send to a customer.
                
                Customer Feedback: {state['feedback']}
                Customer Name: Valued Customer
                Your Name: Usman Ahmad
                Your Title: Customer Service Representative
                
                The email should:
                1. Thank them warmly for their positive feedback
                2. Mention specific positive points from their feedback
                3. Ask for a 5-star review with a review link placeholder
                4. End with your signature
                
                Format as a complete email with subject line.
                """
                
                email_content = self.llm.invoke(email_prompt).content
                
                # Parse subject and body
                lines = email_content.strip().split('\n')
                subject = lines[0].replace('Subject:', '').strip()
                body = '\n'.join(lines[1:]).strip()
                
                # Send the email
                success = send_email_via_smtp(
                    to_email=customer_email,
                    subject=subject,
                    body=body,
                    from_email=Config.FROM_EMAIL,
                    username=self.email_username,
                    password=self.email_password,
                    smtp_server=self.smtp_server,
                    smtp_port=self.smtp_port
                )
                
                if success:
                    state['email_sent'] = True
                    state['action_taken'] = "sent_thank_you_email"
                    logger.info(f"Thank you email sent to {customer_email}")
                else:
                    state['email_sent'] = False
                    state['error'] = "Email sending failed"
                
            except Exception as e:
                logger.error(f"Failed to send thank you email: {str(e)}")
                state['error'] = f"Email send failed: {str(e)}"
                state['email_sent'] = False
                
            return state
        
        def update_state_positive(state: AgentState) -> AgentState:
            state['action_taken'] = "positive_handling_complete"
            return state
        
        # Build LangGraph
        graph = StateGraph(AgentState)
        graph.add_node("send_email", send_thank_you_email)
        graph.add_node("complete", update_state_positive)
        
        graph.set_entry_point("send_email")
        graph.add_edge("send_email", "complete")
        graph.add_edge("complete", END)
        
        return graph.compile()
    
    def create_negative_agent(self):
        """Create agent for negative feedback handling."""
        
        def create_support_ticket(state: AgentState) -> AgentState:
            """Create support ticket and send escalation email."""
            try:
                # Get customer email - use test email if none provided
                customer_email = state.get('customer_email')
                if not customer_email or customer_email == 'customer@example.com':
                    customer_email = TEST_EMAIL
                    logger.info(f"Using test email for negative feedback: {customer_email}")
                
                # Generate ticket using LLM
                ticket_prompt = f"""
                Generate a professional support ticket for this negative feedback.
                
                Feedback: {state['feedback']}
                Customer Email: {customer_email}
                
                Include:
                - Priority level: High
                - Category: Customer Service Issue
                - Description of the issue
                - Suggested next steps
                - Support contact information
                """
                
                ticket_details = self.llm.invoke(ticket_prompt).content
                ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                state['ticket_id'] = ticket_id
                state['action_taken'] = "created_support_ticket"
                
                # Log ticket
                logger.info(f"Support ticket created: {ticket_id}")
                
                # Send escalation email to support team
                escalation_subject = f"URGENT: Customer Issue Ticket {ticket_id}"
                escalation_body = f"""
                New support ticket created for customer feedback.
                
                Ticket ID: {ticket_id}
                Customer Email: {customer_email}
                
                Issue Details:
                {ticket_details}
                
                Please investigate and respond within 24 hours.
                """
                
                send_email_via_smtp(
                    to_email=Config.SUPPORT_EMAIL,
                    subject=escalation_subject,
                    body=escalation_body,
                    from_email=Config.FROM_EMAIL,
                    username=self.email_username,
                    password=self.email_password,
                    smtp_server=self.smtp_server,
                    smtp_port=self.smtp_port
                )
                
                # Also send apology email to customer
                apology_prompt = f"""
                Create a sincere apology email for this negative feedback.
                
                Feedback: {state['feedback']}
                Your Name: Usman Ahmad
                Your Title: Customer Service Representative
                
                The email should:
                1. Apologize sincerely for their experience
                2. Acknowledge their frustration
                3. Assure them their issue is being addressed
                4. Provide ticket reference number
                5. Set expectations for resolution
                6. Include your signature
                
                Format as a complete email with subject line.
                """
                
                apology_content = self.llm.invoke(apology_prompt).content
                
                # Parse subject and body
                lines = apology_content.strip().split('\n')
                subject = lines[0].replace('Subject:', '').strip()
                body = '\n'.join(lines[1:]).strip()
                
                # Send apology email to customer
                send_email_via_smtp(
                    to_email=customer_email,
                    subject=subject,
                    body=body,
                    from_email=Config.FROM_EMAIL,
                    username=self.email_username,
                    password=self.email_password,
                    smtp_server=self.smtp_server,
                    smtp_port=self.smtp_port
                )
                
                logger.info(f"Apology email sent to {customer_email}")
                
            except Exception as e:
                logger.error(f"Failed to create support ticket: {str(e)}")
                state['error'] = f"Ticket creation failed: {str(e)}"
                
            return state
        
        def update_state_negative(state: AgentState) -> AgentState:
            state['action_taken'] = "negative_handling_complete"
            return state
        
        # Build LangGraph
        graph = StateGraph(AgentState)
        graph.add_node("create_ticket", create_support_ticket)
        graph.add_node("complete", update_state_negative)
        
        graph.set_entry_point("create_ticket")
        graph.add_edge("create_ticket", "complete")
        graph.add_edge("complete", END)
        
        return graph.compile()
    
    def _send_email(self, to_email: str, subject: str, body: str):
        """Send email using SMTP."""
        return send_email_via_smtp(
            to_email=to_email,
            subject=subject,
            body=body,
            from_email=self.from_email,
            username=self.email_username,
            password=self.email_password,
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port
        )

# ============================================================================
# EMAIL SENDING FUNCTION
# ============================================================================
def send_email_via_smtp(to_email, subject, body, from_email, username, password, smtp_server, smtp_port):
    """Send email using SMTP with error handling."""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Attach body
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect and send
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            if username and password:
                server.login(username, password)
            server.send_message(msg)
        
        logger.info(f"✅ Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Email sending failed: {str(e)}")
        return False

# Singleton instances
_positive_agent = None
_negative_agent = None

def get_positive_agent():
    global _positive_agent
    if _positive_agent is None:
        _positive_agent = FeedbackAgents().create_positive_agent()
    return _positive_agent

def get_negative_agent():
    global _negative_agent
    if _negative_agent is None:
        _negative_agent = FeedbackAgents().create_negative_agent()
    return _negative_agent