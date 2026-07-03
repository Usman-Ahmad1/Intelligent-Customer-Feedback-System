"""
FeedbackFlow AI - Intelligent Customer Feedback System
Streamlit Interface for Production Deployment
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import time
from typing import Dict, Any, List

# Import the pipeline
from pipeline import get_pipeline
from logging_config import logger

# ============================================================================
# CONFIGURATION - YOUR INFORMATION
# ============================================================================
YOUR_NAME = "Usman Ahmad"
YOUR_EMAIL = "uahmaddatascientist@gmail.com"
SUPPORT_EMAIL = "uahmaddatascientist@gmail.com"
COMPANY_NAME = "FeedbackFlow AI"

# Page Configuration
st.set_page_config(
    page_title="FeedbackFlow AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================
def load_css():
    """Load custom CSS for professional styling."""
    
    st.markdown("""
    <style>
        /* Main container styling */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .main-header h1 {
            font-size: 3rem;
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.5px;
        }
        
        .main-header p {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-top: 0.5rem;
        }
        
        /* Sentiment cards */
        .sentiment-card {
            padding: 1.5rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border-left: 5px solid;
        }
        
        .sentiment-positive {
            background: #d4edda;
            border-left-color: #28a745;
            color: #155724;
        }
        
        .sentiment-negative {
            background: #f8d7da;
            border-left-color: #dc3545;
            color: #721c24;
        }
        
        .sentiment-neutral {
            background: #fff3cd;
            border-left-color: #ffc107;
            color: #856404;
        }
        
        .sentiment-error {
            background: #e2e3e5;
            border-left-color: #6c757d;
            color: #383d41;
        }
        
        /* Response card - UPDATED for better visibility */
        .response-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            margin: 1rem 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            color: #1a1a1a;  /* Dark text for better visibility */
        }
        
        .response-card h4 {
            color: #495057;
            margin-bottom: 0.5rem;
        }
        
        .response-card p {
            color: #1a1a1a;  /* Dark text for paragraphs */
            line-height: 1.8;
        }
        
        /* Action badges */
        .action-badge {
            display: inline-block;
            padding: 0.35rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
            margin: 0.25rem;
        }
        
        .action-success {
            background: #d4edda;
            color: #155724;
        }
        
        .action-warning {
            background: #fff3cd;
            color: #856404;
        }
        
        .action-danger {
            background: #f8d7da;
            color: #721c24;
        }
        
        .action-info {
            background: #d1ecf1;
            color: #0c5460;
        }
        
        /* Metrics cards */
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            border: 1px solid #e9ecef;
            transition: transform 0.2s;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #2c3e50;
        }
        
        .metric-label {
            color: #6c757d;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Feedback display */
        .feedback-text {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            border-left: 3px solid #667eea;
            font-style: italic;
            margin: 0.5rem 0;
            color: #1a1a1a;  /* Dark text for feedback */
        }
        
        /* Sidebar customization */
        .sidebar-section {
            padding: 1rem 0;
            border-bottom: 1px solid #e9ecef;
            margin-bottom: 1rem;
        }
        
        .sidebar-section h3 {
            color: #495057;
            font-size: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        /* Divider */
        .custom-divider {
            height: 2px;
            background: linear-gradient(to right, transparent, #667eea, transparent);
            margin: 2rem 0;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.6rem 2rem;
            border-radius: 50px;
            font-weight: 600;
            transition: all 0.3s;
            width: 100%;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        /* Text area styling */
        .stTextArea > div > div > textarea {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 1rem;
            font-size: 1rem;
        }
        
        .stTextArea > div > div > textarea:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        /* Support email card */
        .support-card {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .support-card h5 {
            color: #dc3545;
            margin-bottom: 0.5rem;
        }
        
        .support-card a {
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }
        
        .support-card a:hover {
            text-decoration: underline;
        }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def get_sentiment_color(sentiment: str) -> str:
    """Get color for sentiment."""
    colors = {
        "POSITIVE": "#28a745",
        "NEGATIVE": "#dc3545",
        "NEUTRAL": "#ffc107"
    }
    return colors.get(sentiment.upper(), "#6c757d")

def get_sentiment_emoji(sentiment: str) -> str:
    """Get emoji for sentiment."""
    emojis = {
        "POSITIVE": "😊",
        "NEGATIVE": "😞",
        "NEUTRAL": "😐"
    }
    return emojis.get(sentiment.upper(), "🤖")

def get_sentiment_class(sentiment: str) -> str:
    """Get CSS class for sentiment."""
    classes = {
        "POSITIVE": "sentiment-positive",
        "NEGATIVE": "sentiment-negative",
        "NEUTRAL": "sentiment-neutral"
    }
    return classes.get(sentiment.upper(), "sentiment-error")

def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display."""
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except:
        return timestamp

def create_sentiment_chart(history: List[Dict]) -> go.Figure:
    """Create a sentiment distribution chart."""
    if not history:
        return go.Figure()
    
    df = pd.DataFrame(history)
    sentiment_counts = df['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']
    
    colors = {
        'POSITIVE': '#28a745',
        'NEGATIVE': '#dc3545', 
        'NEUTRAL': '#ffc107'
    }
    
    fig = px.pie(
        sentiment_counts,
        values='Count',
        names='Sentiment',
        title='Sentiment Distribution',
        color='Sentiment',
        color_discrete_map=colors,
        hole=0.4
    )
    
    fig.update_layout(
        showlegend=True,
        height=350,
        margin=dict(t=40, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#ffffff', width=2))
    )
    
    return fig

def create_timeline_chart(history: List[Dict]) -> go.Figure:
    """Create a timeline of feedback processing."""
    if len(history) < 2:
        return go.Figure()
    
    df = pd.DataFrame(history)
    df['timestamp_dt'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp_dt')
    
    # Map sentiments to numeric for plotting
    sentiment_map = {'POSITIVE': 1, 'NEUTRAL': 0, 'NEGATIVE': -1}
    df['sentiment_value'] = df['sentiment'].map(sentiment_map)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['timestamp_dt'],
        y=df['sentiment_value'],
        mode='lines+markers',
        name='Sentiment Trend',
        line=dict(color='#667eea', width=2),
        marker=dict(
            size=12,
            color=df['sentiment'].map({
                'POSITIVE': '#28a745',
                'NEGATIVE': '#dc3545',
                'NEUTRAL': '#ffc107'
            }),
            symbol='circle'
        ),
        text=df['feedback'],
        hovertemplate='<b>Feedback:</b> %{text}<br>' +
                     '<b>Sentiment:</b> %{customdata}<br>' +
                     '<b>Time:</b> %{x|%H:%M}<extra></extra>',
        customdata=df['sentiment']
    ))
    
    fig.update_layout(
        title='Feedback Timeline',
        xaxis_title='Time',
        yaxis_title='Sentiment',
        height=300,
        margin=dict(t=40, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(
            tickvals=[-1, 0, 1],
            ticktext=['Negative', 'Neutral', 'Positive'],
            range=[-1.5, 1.5]
        ),
        hovermode='x unified'
    )
    
    return fig

# ============================================================================
# MAIN APPLICATION
# ============================================================================
def main():
    """Main Streamlit application."""
    
    # Load CSS
    load_css()
    
    # Initialize session state
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'pipeline' not in st.session_state:
        try:
            st.session_state.pipeline = get_pipeline()
        except Exception as e:
            st.error(f"❌ Failed to initialize pipeline: {str(e)}")
            st.stop()
    if 'feedback_input' not in st.session_state:
        st.session_state.feedback_input = ""
    if 'process_clicked' not in st.session_state:
        st.session_state.process_clicked = False
    
    # ========================================================================
    # SIDEBAR - Configuration & Analytics
    # ========================================================================
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h2 style='color: #667eea;'>🤖 FeedbackFlow</h2>
            <p style='color: #6c757d; font-size: 0.9rem;'>Intelligent Feedback System</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # System Status
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 🟢 System Status")
        st.markdown(f"**Model:** `llama-3.1-8b-instant`")
        st.markdown(f"**Status:** ✅ Operational")
        st.markdown(f"**Processed:** {len(st.session_state.history)} feedbacks")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick Stats
        if st.session_state.history:
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("### 📊 Quick Stats")
            
            df = pd.DataFrame(st.session_state.history)
            
            col1, col2 = st.columns(2)
            with col1:
                positive_count = len(df[df['sentiment'] == 'POSITIVE'])
                st.metric("😊 Positive", positive_count)
            with col2:
                negative_count = len(df[df['sentiment'] == 'NEGATIVE'])
                st.metric("😞 Negative", negative_count)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Export Options
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 💾 Data Export")
        
        if st.button("📥 Export as CSV", use_container_width=True):
            if st.session_state.history:
                df = pd.DataFrame(st.session_state.history)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"feedback_history_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("No data to export")
        
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.history = []
            st.session_state.feedback_input = ""
            st.success("History cleared!")
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Example Feedbacks
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 💡 Try These Examples")
        st.markdown("*Click any example to load it*")
        
        examples = [
            "The product is amazing! It exceeded all my expectations.",
            "Terrible customer service. The product broke in 2 days.",
            "It's okay, does what it says but nothing special.",
            "I absolutely love this! Best purchase I've made this year.",
            "Worst experience ever. Never buying from here again.",
            "The team was very helpful and solved my issue quickly."
        ]
        
        for example in examples:
            button_key = f"example_{hash(example)}"
            if st.button(f"📝 {example[:50]}...", key=button_key, use_container_width=True):
                st.session_state.feedback_input = example
                st.session_state.process_clicked = True
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Support Info - Updated with your info
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 📧 Contact Us")
        st.markdown(f"""
        <div style='font-size: 0.85rem; color: #6c757d;'>
            <p><strong>Support Team:</strong></p>
            <p><strong>{YOUR_NAME}</strong></p>
            <p><a href="mailto:{YOUR_EMAIL}" style="color: #667eea; text-decoration: none;">{YOUR_EMAIL}</a></p>
            <p style='margin-top: 0.5rem; font-size: 0.8rem;'>Response within 24 hours</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer
        st.markdown("---")
        st.markdown(
            f"""
            <div style='text-align: center; color: #6c757d; font-size: 0.8rem;'>
                <p>FeedbackFlow AI v2.0</p>
                <p>Powered by LangChain & Groq</p>
                <p style='margin-top: 0.3rem;'>© 2026 {YOUR_NAME}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # ========================================================================
    # MAIN CONTENT
    # ========================================================================
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 FeedbackFlow AI</h1>
        <p>Intelligent Customer Feedback System with Sentiment Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ========================================================================
    # INPUT SECTION
    # ========================================================================
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📝 Enter Customer Feedback")
        
        feedback = st.text_area(
            "Feedback",
            value=st.session_state.feedback_input,
            placeholder="Type or paste customer feedback here...",
            height=120,
            key="feedback_text_area",
            label_visibility="collapsed"
        )
        
        if feedback != st.session_state.feedback_input:
            st.session_state.feedback_input = feedback
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        process_button = st.button(
            "🚀 Analyze Feedback",
            use_container_width=True,
            type="primary"
        )
    
    # ========================================================================
    # PROCESSING
    # ========================================================================
    should_process = process_button or st.session_state.process_clicked
    
    if should_process and st.session_state.feedback_input:
        st.session_state.process_clicked = False
        
        with st.spinner("🤔 Analyzing feedback..."):
            try:
                result = st.session_state.pipeline.process_feedback(st.session_state.feedback_input)
                st.session_state.history.append(result)
                
                st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
                display_results(result)
                
            except Exception as e:
                st.error(f"❌ Error processing feedback: {str(e)}")
                logger.error(f"Processing error: {str(e)}")
    
    elif should_process and not st.session_state.feedback_input:
        st.warning("⚠️ Please enter some feedback to analyze.")
        st.session_state.process_clicked = False
    
    # ========================================================================
    # ANALYTICS DASHBOARD
    # ========================================================================
    if st.session_state.history:
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📊 Analytics Dashboard")
        
        col1, col2, col3, col4 = st.columns(4)
        df = pd.DataFrame(st.session_state.history)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(df)}</div>
                <div class="metric-label">Total Feedback</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            positive_pct = (len(df[df['sentiment'] == 'POSITIVE']) / len(df) * 100) if len(df) > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #28a745;">{positive_pct:.1f}%</div>
                <div class="metric-label">Positive</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            negative_pct = (len(df[df['sentiment'] == 'NEGATIVE']) / len(df) * 100) if len(df) > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #dc3545;">{negative_pct:.1f}%</div>
                <div class="metric-label">Negative</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            actions = df['action_taken'].value_counts().to_dict()
            unique_actions = len(actions)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{unique_actions}</div>
                <div class="metric-label">Action Types</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            sentiment_chart = create_sentiment_chart(st.session_state.history)
            if sentiment_chart:
                st.plotly_chart(sentiment_chart, use_container_width=True, key="sentiment_chart")
        
        with col2:
            timeline_chart = create_timeline_chart(st.session_state.history)
            if timeline_chart:
                st.plotly_chart(timeline_chart, use_container_width=True, key="timeline_chart")
        
        # Recent History
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📋 Recent Feedback")
        
        recent = st.session_state.history[-5:][::-1]
        
        for i, item in enumerate(recent):
            sentiment = item.get('sentiment', 'UNKNOWN')
            emoji = get_sentiment_emoji(sentiment)
            
            with st.expander(f"{emoji} Feedback #{len(st.session_state.history) - i} - {format_timestamp(item.get('timestamp', ''))}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="feedback-text">
                        "{item.get('feedback', 'N/A')}"
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="response-card">
                        <h4>💬 Response</h4>
                        <p>{item.get('response', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    sentiment_class = get_sentiment_class(sentiment)
                    st.markdown(f"""
                    <div class="sentiment-card {sentiment_class}">
                        <strong>Sentiment:</strong> {emoji} {sentiment}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    action_taken = item.get('action_taken', 'none')
                    action_class = {
                        'sent_thank_you_email': 'action-success',
                        'positive_handling_complete': 'action-success',
                        'created_support_ticket': 'action-danger',
                        'suggested_support_contact': 'action-warning',
                        'negative_handling_complete': 'action-warning',
                        'neutral_handled': 'action-info'
                    }.get(action_taken, 'action-info')
                    
                    st.markdown(f"""
                    <div style="margin-top: 0.5rem;">
                        <span class="action-badge {action_class}">
                            ⚡ {action_taken.replace('_', ' ').title()}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if item.get('ticket_id'):
                        st.info(f"🎫 Ticket: {item['ticket_id']}")
                    
                    if item.get('email_sent'):
                        st.success("📧 Email Sent")
                    
                    if item.get('has_error'):
                        st.error(f"⚠️ Error: {item.get('error_details', 'Unknown')}")

# ============================================================================
# RESULTS DISPLAY FUNCTION - UPDATED WITH YOUR INFO
# ============================================================================
def display_results(result: Dict[str, Any]):
    """Display processing results in a beautiful format."""
    
    st.markdown("### ✨ Analysis Results")
    
    # Sentiment
    sentiment = result.get('sentiment', 'UNKNOWN')
    emoji = get_sentiment_emoji(sentiment)
    sentiment_class = get_sentiment_class(sentiment)
    
    st.markdown(f"""
    <div class="sentiment-card {sentiment_class} fade-in">
        <strong>Sentiment Analysis:</strong> {emoji} {sentiment}
    </div>
    """, unsafe_allow_html=True)
    
    # Response
    response = result.get('response', 'No response generated.')
    
    # Replace [Your Name] with YOUR_NAME in the response
    response = response.replace('[Your Name]', YOUR_NAME)
    response = response.replace('Your Name', YOUR_NAME)
    response = response.replace('your name', YOUR_NAME)
    
    st.markdown(f"""
    <div class="response-card fade-in">
        <h4>💬 Generated Response</h4>
        <p style="font-size: 1.05rem; line-height: 1.6;">{response}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # If negative sentiment, show support contact with YOUR information
    if sentiment == 'NEGATIVE':
        st.markdown(f"""
        <div class="support-card fade-in">
            <h5>📧 Need Further Assistance?</h5>
            <p>We apologize for your experience. Our support team is here to help:</p>
            <ul>
                <li><strong>Support Representative:</strong> {YOUR_NAME}</li>
                <li><strong>Email:</strong> <a href="mailto:{YOUR_EMAIL}">{YOUR_EMAIL}</a></li>
                <li><strong>Response Time:</strong> Within 24 hours</li>
                <li><strong>Priority:</strong> Your issue has been escalated</li>
            </ul>
            <p style="margin-top: 0.5rem; color: #6c757d; font-size: 0.9rem;">
                ⏰ We typically respond within 24 business hours.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # If positive sentiment, show appreciation with YOUR name
    if sentiment == 'POSITIVE':
        st.markdown(f"""
        <div style="background: #d4edda; border-radius: 10px; padding: 1rem; margin: 0.5rem 0; border-left: 5px solid #28a745;">
            <p style="margin: 0; color: #155724;">
                🌟 Thank you for your positive feedback! We truly appreciate your support.
                <br><small style="color: #155724;">- {YOUR_NAME}, Customer Service Team</small>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Actions
    st.markdown("#### 🎯 Actions Taken")
    
    cols = st.columns(3)
    
    with cols[0]:
        action_taken = result.get('action_taken', 'none')
        action_labels = {
            'sent_thank_you_email': '📧 Thank You Email',
            'positive_handling_complete': '✅ Positive Handling',
            'created_support_ticket': '🎫 Support Ticket',
            'suggested_support_contact': '💬 Support Suggestion',
            'negative_handling_complete': '🔄 Negative Handling',
            'neutral_handled': '➖ Neutral Handling',
            'pending': '⏳ Pending'
        }
        st.info(f"**Action:** {action_labels.get(action_taken, action_taken)}")
    
    with cols[1]:
        if result.get('ticket_id'):
            st.warning(f"**Ticket ID:** {result['ticket_id']}")
        else:
            st.info("**Ticket:** N/A")
    
    with cols[2]:
        if result.get('email_sent'):
            st.success("📧 Email: Sent")
        else:
            st.info("📧 Email: Not Required")
    
    # Error handling
    if result.get('has_error'):
        st.error(f"⚠️ {result.get('error_details', 'An error occurred')}")
    
    # Timestamp
    timestamp = result.get('timestamp', datetime.now().isoformat())
    st.caption(f"🕐 Processed at: {format_timestamp(timestamp)}")
    
    # Save to log option
    if st.button("💾 Save to Log"):
        try:
            from utils import feedback_utils
            feedback_utils.save_to_log(result)
            st.success("✅ Saved to log file!")
        except Exception as e:
            st.error(f"❌ Failed to save log: {str(e)}")

# ============================================================================
# RUN APPLICATION
# ============================================================================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ Application error: {str(e)}")
        logger.error(f"Application error: {str(e)}", exc_info=True)