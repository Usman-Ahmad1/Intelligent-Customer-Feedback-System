from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, Any
import re

from config import Config
from logging_config import logger


class FeedbackChains:
    """Manages all LangChain chains for feedback processing using Groq."""
    
    def __init__(self):
        # Initialize Groq LLM
        self.llm = ChatGroq(
            model=Config.GROQ_MODEL,
            temperature=0.0,          # Low temperature for reliable sentiment analysis
            api_key=Config.GROQ_API_KEY
        )
        logger.info(f"✅ Groq LLM initialized with model: {Config.GROQ_MODEL}")
        
        self._initialize_chains()
        
    def _initialize_chains(self):
        """Initialize all processing chains."""
        
        # 1. Sentiment Analysis Chain
        sentiment_prompt = ChatPromptTemplate.from_template(
            """You are a sentiment analysis expert. Analyze the customer feedback and classify it.

CRITICAL RULES:
- Return ONLY ONE WORD: POSITIVE, NEGATIVE, or NEUTRAL
- Do NOT add any explanation, punctuation, or extra text

EXAMPLES:
- "I love this product!" → POSITIVE
- "This is terrible service" → NEGATIVE
- "It works as expected" → NEUTRAL

Feedback: {feedback}

Classification (ONLY ONE WORD):"""
        )
        self.sentiment_chain = sentiment_prompt | self.llm | StrOutputParser()
        
        # 2. Positive Response Chain
        positive_prompt = ChatPromptTemplate.from_template(
            """You are a friendly customer service representative. Write a warm, genuine thank you 
            response for this positive feedback. Be appreciative and professional.

Feedback: {feedback}

Response:"""
        )
        self.positive_chain = positive_prompt | self.llm | StrOutputParser()
        
        # 3. Negative Response Chain
        negative_prompt = ChatPromptTemplate.from_template(
            """You are a caring customer service representative. Write a sincere apology 
            for this negative feedback. Show empathy and understanding.

Feedback: {feedback}

Response:"""
        )
        self.negative_chain = negative_prompt | self.llm | StrOutputParser()
        
        # 4. Neutral Response Chain
        neutral_prompt = ChatPromptTemplate.from_template(
            """You are a professional customer service representative. Write a polite, balanced 
            response to this neutral feedback. Thank them for their input.

Feedback: {feedback}

Response:"""
        )
        self.neutral_chain = neutral_prompt | self.llm | StrOutputParser()
        
        logger.info("✅ All feedback chains initialized successfully with Groq.")
    
    def clean_sentiment(self, sentiment: str) -> str:
        """Clean and normalize sentiment output."""
        if not sentiment:
            return "NEUTRAL"
        
        sentiment = sentiment.strip().upper()
        sentiment = re.sub(r'[^A-Z\s]', '', sentiment)  # Remove special characters
        
        if "POSITIVE" in sentiment:
            return "POSITIVE"
        elif "NEGATIVE" in sentiment:
            return "NEGATIVE"
        elif "NEUTRAL" in sentiment:
            return "NEUTRAL"
        
        # Fallback keyword check
        positive_words = ["GOOD", "GREAT", "EXCELLENT", "LOVE", "HAPPY", "SATISFIED"]
        negative_words = ["BAD", "TERRIBLE", "POOR", "AWFUL", "HATE", "DISAPPOINTED"]
        
        if any(word in sentiment for word in positive_words):
            return "POSITIVE"
        if any(word in sentiment for word in negative_words):
            return "NEGATIVE"
        
        logger.warning(f"Could not parse sentiment: '{sentiment}'. Defaulting to NEUTRAL.")
        return "NEUTRAL"
    
    def classify_feedback(self, feedback: str) -> str:
        """Classify feedback sentiment."""
        try:
            logger.info(f"Classifying feedback: {feedback[:60]}...")
            
            raw_sentiment = self.sentiment_chain.invoke({"feedback": feedback})
            logger.info(f"Raw sentiment: '{raw_sentiment}'")
            
            clean_sentiment = self.clean_sentiment(raw_sentiment)
            logger.info(f"Final sentiment: {clean_sentiment}")
            
            return clean_sentiment
            
        except Exception as e:
            logger.error(f"Sentiment classification failed: {str(e)}")
            return "NEUTRAL"
    
    def generate_response(self, sentiment: str, feedback: str) -> str:
        """Generate appropriate response based on sentiment."""
        try:
            chain_map = {
                "POSITIVE": self.positive_chain,
                "NEGATIVE": self.negative_chain,
                "NEUTRAL": self.neutral_chain
            }
            
            chain = chain_map.get(sentiment, self.neutral_chain)
            response = chain.invoke({"feedback": feedback})
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            return "Thank you for your feedback. We appreciate your input."


# Singleton instance
_feedback_chains = None

def get_feedback_chains() -> FeedbackChains:
    """Get or create the FeedbackChains singleton."""
    global _feedback_chains
    if _feedback_chains is None:
        _feedback_chains = FeedbackChains()
    return _feedback_chains