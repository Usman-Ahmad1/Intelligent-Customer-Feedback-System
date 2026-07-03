import json
from datetime import datetime
from typing import Dict, Any

class FeedbackUtils:
    """Utility functions for feedback processing."""
    
    @staticmethod
    def format_summary(result: Dict[str, Any]) -> str:
        """Format processing result as a readable summary."""
        summary = [
            "=" * 50,
            "FEEDBACK PROCESSING SUMMARY",
            "=" * 50,
            f"Timestamp: {result.get('timestamp', datetime.now().isoformat())}",
            f"Sentiment: {result.get('sentiment', 'UNKNOWN')}",
            f"Action: {result.get('action_taken', 'NONE')}",
        ]
        
        if result.get('ticket_id'):
            summary.append(f"Ticket: {result['ticket_id']}")
        if result.get('email_sent'):
            summary.append("Email: Sent")
        if result.get('has_error'):
            summary.append(f"Error: {result.get('error_details', 'Unknown')}")
            
        summary.append("=" * 50)
        return "\n".join(summary)
    
    @staticmethod
    def save_to_log(result: Dict[str, Any], log_file: str = "feedback_log.json"):
        """Save processing result to a JSON log file."""
        try:
            # Append to log file
            with open(log_file, 'a', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
                f.write('\n')
            return True
        except Exception as e:
            print(f"Failed to save log: {e}")
            return False

# Create utils instance
feedback_utils = FeedbackUtils()