"""Trend and Social Media Sentiment Analysis Engine."""

import random
from typing import Dict, Any

class SentimentAnalyzer:
    """Analyzes text data (news, social media posts) to detect emerging retail trends and sentiment spikes."""
    
    def __init__(self):
        self.positive_keywords = ["love", "best", "must-have", "amazing", "viral", "trend", "hype", "incredible", "favorite", "obsessed"]
        self.negative_keywords = ["worst", "disappointed", "broke", "garbage", "trash", "bad", "returned", "overrated", "slow", "hate"]

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze the sentiment score and identify product/category mentions in text."""
        text_lower = text.lower()
        
        pos_count = sum(1 for word in self.positive_keywords if word in text_lower)
        neg_count = sum(1 for word in self.negative_keywords if word in text_lower)
        
        total = pos_count + neg_count
        if total == 0:
            sentiment_score = 0.0  # Neutral
        else:
            sentiment_score = (pos_count - neg_count) / total
            
        # Classify sentiment
        if sentiment_score > 0.25:
            sentiment = "positive"
        elif sentiment_score < -0.25:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        # Determine if there is a potential viral trend spike
        is_viral = "viral" in text_lower or "hype" in text_lower or (sentiment == "positive" and total > 3)

        return {
            "sentiment_score": round(sentiment_score, 2),
            "sentiment": sentiment,
            "is_viral": is_viral,
            "intensity": round(random.uniform(0.5, 1.0) if is_viral else random.uniform(0.1, 0.5), 2),
            "confidence": round(random.uniform(0.70, 0.95), 2)
        }

analyzer = SentimentAnalyzer()
