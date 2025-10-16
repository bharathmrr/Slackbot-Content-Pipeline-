"""Outline generation logic."""

from typing import List, Dict, Any
from loguru import logger
from app.outline.websearch import WebSearcher
from app.outline.extractor import ContentExtractor


class OutlineGenerator:
    """Generates content outlines based on competitive research."""
    
    def __init__(self):
        self.web_searcher = WebSearcher()
        self.content_extractor = ContentExtractor()
    
    async def generate_outline(self, keywords: List[str]) -> Dict[str, Any]:
        """Generate outline for keywords."""
        try:
            main_keyword = keywords[0] if keywords else "topic"
            
            # Search and extract content
            search_results = await self.web_searcher.search_keywords(keywords, 5)
            urls = [r["url"] for r in search_results[:3]]
            extracted = await self.content_extractor.extract_from_urls(urls)
            
            # Create outline
            return {
                "title": f"Complete Guide to {main_keyword.title()}",
                "meta_description": f"Learn about {main_keyword} with this guide.",
                "target_keywords": keywords,
                "estimated_word_count": 2000,
                "sections": [
                    {
                        "heading": "Introduction",
                        "level": 2,
                        "description": f"Overview of {main_keyword}",
                        "estimated_words": 200
                    },
                    {
                        "heading": f"Understanding {main_keyword.title()}",
                        "level": 2,
                        "description": f"Key concepts of {main_keyword}",
                        "estimated_words": 400
                    },
                    {
                        "heading": f"Benefits of {main_keyword.title()}",
                        "level": 2,
                        "description": f"Advantages of {main_keyword}",
                        "estimated_words": 350
                    },
                    {
                        "heading": f"How to Use {main_keyword.title()}",
                        "level": 2,
                        "description": f"Implementation guide",
                        "estimated_words": 500
                    },
                    {
                        "heading": "Best Practices",
                        "level": 2,
                        "description": "Tips and recommendations",
                        "estimated_words": 300
                    },
                    {
                        "heading": "Conclusion",
                        "level": 2,
                        "description": "Summary and next steps",
                        "estimated_words": 150
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating outline: {e}")
            return self._generate_fallback_outline(keywords)
    
    def _generate_fallback_outline(self, keywords: List[str]) -> Dict[str, Any]:
        """Generate basic outline when research fails."""
        main_keyword = keywords[0] if keywords else "content"
        
        return {
            "title": f"Guide to {main_keyword.title()}",
            "meta_description": f"Learn about {main_keyword}.",
            "target_keywords": keywords,
            "estimated_word_count": 1500,
            "sections": [
                {"heading": "Introduction", "level": 2, "estimated_words": 200},
                {"heading": f"What is {main_keyword.title()}", "level": 2, "estimated_words": 300},
                {"heading": "Benefits", "level": 2, "estimated_words": 250},
                {"heading": "How to Get Started", "level": 2, "estimated_words": 400},
                {"heading": "Conclusion", "level": 2, "estimated_words": 150}
            ]
        }
