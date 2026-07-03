from langchain_core.runnables import RunnableBranch, RunnablePassthrough, RunnableLambda
from langchain_core.runnables import RunnableParallel
from typing import Dict, Any
from datetime import datetime
import json

from chains import get_feedback_chains
from agents import get_positive_agent, get_negative_agent
from logging_config import logger

class FeedbackPipeline:
    """Main feedback processing pipeline using LCEL."""
    
    def __init__(self):
        self.chains = get_feedback_chains()
        self.positive_agent = get_positive_agent()
        self.negative_agent = get_negative_agent()
        self._build_pipeline()
        
    def _route_by_sentiment(self, state: Dict[str, Any]) -> str:
        """Route to appropriate branch based on sentiment."""
        sentiment = state.get("sentiment", "NEUTRAL").upper()
        
        if sentiment == "POSITIVE":
            return "positive"
        elif sentiment == "NEGATIVE":
            return "negative"
        else:
            return "neutral"
    
    def _prepare_state(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare state for agents."""
        return {
            "feedback": input_data.get("feedback", ""),
            "sentiment": input_data.get("sentiment", "NEUTRAL"),
            "response": input_data.get("response", ""),
            "action_taken": "pending",
            "ticket_id": None,
            "email_sent": False,
            "error": ""
        }
    
    def _handle_positive_flow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle positive feedback flow with agent."""
        try:
            logger.info(f"Starting positive flow for feedback: {state['feedback'][:50]}...")
            result = self.positive_agent.invoke(state)
            logger.info("Positive flow completed successfully")
            return result
        except Exception as e:
            logger.error(f"Positive flow failed: {str(e)}")
            state['error'] = f"Positive agent failed: {str(e)}"
            return state
    
    def _handle_negative_flow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle negative feedback flow with agent."""
        try:
            logger.info(f"Starting negative flow for feedback: {state['feedback'][:50]}...")
            result = self.negative_agent.invoke(state)
            logger.info("Negative flow completed successfully")
            return result
        except Exception as e:
            logger.error(f"Negative flow failed: {str(e)}")
            state['error'] = f"Negative agent failed: {str(e)}"
            return state
    
    def _generate_summary(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive summary of processing."""
        return {
            "timestamp": datetime.now().isoformat(),
            "feedback": state.get("feedback", ""),
            "sentiment": state.get("sentiment", "NEUTRAL"),
            "response": state.get("response", ""),
            "action_taken": state.get("action_taken", "none"),
            "ticket_id": state.get("ticket_id", "N/A"),
            "email_sent": state.get("email_sent", False),
            "has_error": bool(state.get("error")),
            "error_details": state.get("error", None)
        }
    
    def _build_pipeline(self):
        """Build the complete LCEL pipeline."""
        
        # Step 1: Classify sentiment
        classify_step = RunnableLambda(
            lambda x: {
                "feedback": x.get("feedback", ""),
                "sentiment": self.chains.classify_feedback(x.get("feedback", ""))
            }
        )
        
        # Step 2: Generate response based on sentiment
        generate_response_step = RunnableLambda(
            lambda x: {
                **x,
                "response": self.chains.generate_response(
                    x.get("sentiment", "NEUTRAL"),
                    x.get("feedback", "")
                )
            }
        )
        
        # Step 3: Route to appropriate handler
        routing_step = RunnableLambda(
            lambda x: {
                **x,
                "route": self._route_by_sentiment(x)
            }
        )
        
        # Step 4: Branch based on sentiment
        branch = RunnableBranch(
            (lambda x: x["route"] == "positive", 
             RunnableLambda(self._handle_positive_flow)),
            (lambda x: x["route"] == "negative", 
             RunnableLambda(self._handle_negative_flow)),
            # Default: neutral
            RunnableLambda(lambda x: {**x, "action_taken": "neutral_handled"})
        )
        
        # Step 5: Generate summary
        summary_step = RunnableLambda(self._generate_summary)
        
        # Build the complete pipeline
        self.pipeline = (
            classify_step
            | generate_response_step
            | routing_step
            | branch
            | summary_step
        )
        
        logger.info("Feedback pipeline built successfully")
    
    def process_feedback(self, feedback: str) -> Dict[str, Any]:
        """
        Process customer feedback through the complete pipeline.
        
        Args:
            feedback: Customer feedback text
            
        Returns:
            Dictionary with processing summary and results
        """
        try:
            if not feedback or not isinstance(feedback, str):
                raise ValueError("Feedback must be a non-empty string")
            
            logger.info(f"Processing feedback: {feedback[:100]}...")
            result = self.pipeline.invoke({"feedback": feedback})
            
            # Log result summary
            logger.info(
                f"Feedback processed - Sentiment: {result['sentiment']}, "
                f"Action: {result['action_taken']}, "
                f"Error: {result['has_error']}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline processing failed: {str(e)}")
            return {
                "error": f"Processing failed: {str(e)}",
                "feedback": feedback,
                "sentiment": "ERROR",
                "timestamp": datetime.now().isoformat()
            }

# Singleton instance
_pipeline = None

def get_pipeline() -> FeedbackPipeline:
    """Get or create the FeedbackPipeline singleton."""
    global _pipeline
    if _pipeline is None:
        _pipeline = FeedbackPipeline()
    return _pipeline