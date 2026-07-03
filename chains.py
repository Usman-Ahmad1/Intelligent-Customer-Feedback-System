from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, Any
import re

from config import Config
from logging_config import logger

class FeedbackChains:
    """Manages all LangChain chains for feedback processing using Groq."""
    
    def __init__(self):
        # Initialize LLM based on provider
        if Config.MODEL_PROVIDER == "groq":
            self.llm = ChatGroq(
                model=Config.GROQ_MODEL,
                temperature=0.0,  # Lower temperature for consistent sentiment analysis
                api_key=Config.GROQ_API_KEY
            )
            logger.info(f"Using Groq with model: {Config.GROQ_MODEL}")
        else:
            self.llm = ChatOpenAI(
                model=Config.OPENAI_MODEL,
                temperature=0.0,
                api_key=Config.OPENAI_API_KEY
            )
            logger.info(f"Using OpenAI with model: {Config.OPENAI_MODEL}")
        
        self._initialize_chains()
        
    def _initialize_chains(self):
        """Initialize all processing chains."""
        
        # 1. Sentiment Analysis Chain - IMPROVED with clearer instructions
        sentiment_prompt = ChatPromptTemplate.from_template(
            """You are a sentiment analysis expert. Analyze the customer feedback and classify it.

CRITICAL RULES:
- Return ONLY ONE WORD: POSITIVE, NEGATIVE, or NEUTRAL
- Do NOT add any explanation, punctuation, or extra text
- POSITIVE: Customer is happy, satisfied, complimentary, or expresses approval
- NEGATIVE: Customer is unhappy, dissatisfied, critical, or expresses complaint
- NEUTRAL: Customer is indifferent, factual, mixed feelings, or neither positive nor negative

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
            """You are a customer service representative. Write a warm, appreciative response 
            to this positive customer feedback. Be genuine and thank them specifically.

Feedback: {feedback}

Your warm, professional response:"""
        )
        self.positive_chain = positive_prompt | self.llm | StrOutputParser()
        
        # 3. Negative Response Chain
        negative_prompt = ChatPromptTemplate.from_template(
            """You are a customer service representative. Write a sincere, empathetic apology 
            to this negative customer feedback. Acknowledge their frustration and show 
            understanding without making excuses.

Feedback: {feedback}

Your sincere, empathetic response:"""
        )
        self.negative_chain = negative_prompt | self.llm | StrOutputParser()
        
        # 4. Neutral Response Chain
        neutral_prompt = ChatPromptTemplate.from_template(
            """You are a customer service representative. Write a professional, balanced 
            response to this neutral customer feedback. Acknowledge their input and 
            thank them for sharing.

Feedback: {feedback}

Your professional, balanced response:"""
        )
        self.neutral_chain = neutral_prompt | self.llm | StrOutputParser()
        
        logger.info(f"All LangChain chains initialized successfully with {Config.MODEL_PROVIDER}")
    
    def clean_sentiment(self, sentiment: str) -> str:
        """Clean and normalize sentiment output with better extraction."""
        if not sentiment:
            logger.warning("Empty sentiment received, defaulting to NEUTRAL")
            return "NEUTRAL"
        
        # Clean the text
        sentiment = sentiment.strip().upper()
        
        # Remove quotes, extra spaces, and punctuation
        sentiment = sentiment.strip('"\'.,!? ')
        
        # Try to find POSITIVE, NEGATIVE, or NEUTRAL as whole words
        patterns = [
            (r'\bPOSITIVE\b', "POSITIVE"),
            (r'\bNEGATIVE\b', "NEGATIVE"),
            (r'\bNEUTRAL\b', "NEUTRAL"),
            # Handle shorthand
            (r'\bPOS\b', "POSITIVE"),
            (r'\bNEG\b', "NEGATIVE"),
            (r'\bNEUT\b', "NEUTRAL"),
            # Handle common positive variations
            (r'\bGOOD\b', "POSITIVE"),
            (r'\bGREAT\b', "POSITIVE"),
            (r'\bEXCELLENT\b', "POSITIVE"),
            (r'\bAMAZING\b', "POSITIVE"),
            (r'\bHAPPY\b', "POSITIVE"),
            (r'\bSATISFIED\b', "POSITIVE"),
            (r'\bLOVE\b', "POSITIVE"),
            # Handle common negative variations
            (r'\bBAD\b', "NEGATIVE"),
            (r'\bPOOR\b', "NEGATIVE"),
            (r'\bTERRIBLE\b', "NEGATIVE"),
            (r'\bAWFUL\b', "NEGATIVE"),
            (r'\bWORST\b', "NEGATIVE"),
            (r'\bHATE\b', "NEGATIVE"),
            (r'\bDISAPPOINTED\b', "NEGATIVE"),
            (r'\bFRUSTRATED\b', "NEGATIVE"),
        ]
        
        for pattern, result in patterns:
            if re.search(pattern, sentiment):
                logger.info(f"Sentiment matched pattern: {result}")
                return result
        
        # Check if the entire text is just one word
        words = sentiment.split()
        if len(words) == 1:
            word = words[0]
            # Check for positive/negative words
            positive_words = ['POSITIVE', 'POS', 'GOOD', 'GREAT', 'EXCELLENT', 'HAPPY', 'SATISFIED']
            negative_words = ['NEGATIVE', 'NEG', 'BAD', 'POOR', 'TERRIBLE', 'AWFUL', 'WORST']
            
            if word in positive_words:
                return "POSITIVE"
            if word in negative_words:
                return "NEGATIVE"
        
        # Log the raw sentiment for debugging
        logger.warning(f"Could not parse sentiment from: '{sentiment}', defaulting to NEUTRAL")
        return "NEUTRAL"
    
    def classify_feedback(self, feedback: str) -> str:
        """Classify feedback sentiment with error handling and debug logging."""
        try:
            logger.info(f"Classifying feedback: {feedback[:50]}...")
            
            # Get raw sentiment
            raw_sentiment = self.sentiment_chain.invoke({"feedback": feedback})
            logger.info(f"Raw sentiment output: '{raw_sentiment}'")
            
            # Clean and normalize
            clean_sentiment = self.clean_sentiment(raw_sentiment)
            logger.info(f"Cleaned sentiment: {clean_sentiment}")
            
            return clean_sentiment
            
        except Exception as e:
            logger.error(f"Sentiment classification failed: {str(e)}")
            return "NEUTRAL"  # Safe fallback
    
    def generate_response(self, sentiment: str, feedback: str) -> str:
        """Generate appropriate response based on sentiment."""
        try:
            logger.info(f"Generating response for {sentiment} feedback")
            
            chain_map = {
                "POSITIVE": self.positive_chain,
                "NEGATIVE": self.negative_chain,
                "NEUTRAL": self.neutral_chain
            }
            
            chain = chain_map.get(sentiment, self.neutral_chain)
            response = chain.invoke({"feedback": feedback})
            
            logger.info(f"Response generated successfully")
            return response
            
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