"""
Debug script to test sentiment analysis
"""
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

def test_sentiment():
    """Test sentiment analysis with various inputs."""
    
    # Initialize LLM
    llm = ChatGroq(
        model="mixtral-8x7b-32768",
        temperature=0.0,  # Lower temperature for consistency
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    # Sentiment prompt
    sentiment_prompt = ChatPromptTemplate.from_template(
        "Analyze this customer feedback and classify it as POSITIVE, NEGATIVE, or NEUTRAL. "
        "Return ONLY one word (POSITIVE/NEGATIVE/NEUTRAL). Do not add any other text.\n\n"
        "Feedback: {feedback}\n\n"
        "Sentiment (ONLY one word):"
    )
    
    chain = sentiment_prompt | llm | StrOutputParser()
    
    # Test cases
    test_cases = [
        ("it is not good", "Should be NEGATIVE"),
        ("i am happy from this service", "Should be POSITIVE"),
        ("this service is bad", "Should be NEGATIVE"),
        ("The product is amazing!", "Should be POSITIVE"),
        ("Terrible customer service", "Should be NEGATIVE"),
        ("It's okay, nothing special", "Should be NEUTRAL"),
        ("I love this product!", "Should be POSITIVE"),
        ("Worst experience ever", "Should be NEGATIVE"),
    ]
    
    print("=" * 60)
    print("🧪 Testing Sentiment Analysis")
    print("=" * 60)
    
    for feedback, expected in test_cases:
        try:
            result = chain.invoke({"feedback": feedback})
            print(f"📝 Feedback: {feedback}")
            print(f"🎯 Result: '{result}'")
            print(f"✅ Expected: {expected}")
            print("-" * 40)
        except Exception as e:
            print(f"❌ Error: {e}")
            print("-" * 40)

if __name__ == "__main__":
    test_sentiment()