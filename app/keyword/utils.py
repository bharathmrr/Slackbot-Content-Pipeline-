"""
Utility functions for keyword processing.
"""

import re
import string
from typing import List, Dict, Set
from collections import Counter


class KeywordUtils:
    """Utility functions for keyword analysis and processing."""
    
    @staticmethod
    def extract_ngrams(text: str, n: int = 2) -> List[str]:
        """Extract n-grams from text."""
        words = text.lower().split()
        if len(words) < n:
            return []
        return [' '.join(words[i:i+n]) for i in range(len(words) - n + 1)]
    
    @staticmethod
    def calculate_keyword_difficulty(keyword: str) -> Dict[str, any]:
        """Calculate basic keyword difficulty metrics."""
        word_count = len(keyword.split())
        char_count = len(keyword)
        
        # Simple difficulty scoring
        difficulty_score = 0
        if word_count == 1:
            difficulty_score += 30  # Single words are competitive
        elif word_count == 2:
            difficulty_score += 20
        else:
            difficulty_score += 10  # Long-tail keywords are easier
        
        if char_count < 10:
            difficulty_score += 20
        elif char_count > 30:
            difficulty_score -= 10
        
        return {
            "keyword": keyword,
            "word_count": word_count,
            "character_count": char_count,
            "difficulty_score": min(100, max(0, difficulty_score)),
            "type": "short-tail" if word_count <= 2 else "long-tail"
        }
    
    @staticmethod
    def find_keyword_themes(keywords: List[str]) -> Dict[str, List[str]]:
        """Find common themes in keywords."""
        themes = {}
        
        # Extract all words
        all_words = []
        for keyword in keywords:
            words = [w.lower() for w in keyword.split() if len(w) > 2]
            all_words.extend(words)
        
        # Find most common words
        word_counts = Counter(all_words)
        common_words = [word for word, count in word_counts.most_common(10) if count > 1]
        
        # Group keywords by common words
        for word in common_words:
            themes[word] = [kw for kw in keywords if word in kw.lower()]
        
        return themes
    
    @staticmethod
    def suggest_related_keywords(keyword: str, existing_keywords: List[str]) -> List[str]:
        """Suggest related keywords based on existing ones."""
        suggestions = []
        base_words = keyword.lower().split()
        
        for existing in existing_keywords:
            existing_words = existing.lower().split()
            
            # Find keywords with overlapping words
            overlap = set(base_words) & set(existing_words)
            if overlap and existing != keyword:
                suggestions.append(existing)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    @staticmethod
    def clean_keyword_list(keywords: List[str]) -> List[str]:
        """Advanced cleaning of keyword list."""
        cleaned = []
        seen = set()
        
        for keyword in keywords:
            # Basic cleaning
            clean_kw = keyword.strip().lower()
            clean_kw = re.sub(r'\s+', ' ', clean_kw)
            clean_kw = re.sub(r'[^\w\s-]', '', clean_kw)
            
            if clean_kw and clean_kw not in seen and len(clean_kw) > 1:
                cleaned.append(clean_kw)
                seen.add(clean_kw)
        
        return cleaned
    
    @staticmethod
    def analyze_keyword_intent(keyword: str) -> str:
        """Analyze search intent of a keyword."""
        keyword_lower = keyword.lower()
        
        # Informational intent
        info_words = ['what', 'how', 'why', 'when', 'where', 'guide', 'tutorial', 'tips']
        if any(word in keyword_lower for word in info_words):
            return "informational"
        
        # Commercial intent
        commercial_words = ['best', 'top', 'review', 'compare', 'vs', 'alternative']
        if any(word in keyword_lower for word in commercial_words):
            return "commercial"
        
        # Transactional intent
        transactional_words = ['buy', 'purchase', 'order', 'price', 'cost', 'cheap', 'discount']
        if any(word in keyword_lower for word in transactional_words):
            return "transactional"
        
        # Navigational intent
        navigational_words = ['login', 'sign in', 'website', 'official', 'homepage']
        if any(word in keyword_lower for word in navigational_words):
            return "navigational"
        
        return "informational"  # Default
    
    @staticmethod
    def get_keyword_variations(keyword: str) -> List[str]:
        """Generate keyword variations."""
        variations = []
        words = keyword.split()
        
        if len(words) > 1:
            # Reorder words
            variations.append(' '.join(reversed(words)))
            
            # Add question format
            variations.append(f"what is {keyword}")
            variations.append(f"how to {keyword}")
            variations.append(f"{keyword} guide")
            variations.append(f"{keyword} tips")
            variations.append(f"best {keyword}")
        
        return variations
    
    @staticmethod
    def calculate_keyword_density(text: str, keyword: str) -> float:
        """Calculate keyword density in text."""
        if not text or not keyword:
            return 0.0
        
        text_words = text.lower().split()
        keyword_words = keyword.lower().split()
        
        if len(keyword_words) == 1:
            # Single word keyword
            count = text_words.count(keyword_words[0])
        else:
            # Multi-word keyword
            count = 0
            for i in range(len(text_words) - len(keyword_words) + 1):
                if text_words[i:i+len(keyword_words)] == keyword_words:
                    count += 1
        
        total_words = len(text_words)
        return (count / total_words * 100) if total_words > 0 else 0.0
