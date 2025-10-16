"""
AI-powered post idea generation for keyword groups.
"""

from typing import List, Dict, Any
from loguru import logger


class PostIdeaGenerator:
    """Generates creative post ideas for keyword clusters."""
    
    def __init__(self):
        self.idea_templates = [
            "Ultimate Guide to {keyword}",
            "10 Best {keyword} Tips for Beginners",
            "How to Master {keyword} in 2024",
            "{keyword}: Everything You Need to Know",
            "Common {keyword} Mistakes to Avoid",
            "The Complete {keyword} Checklist",
            "{keyword} vs Alternatives: Which is Better?",
            "5 {keyword} Strategies That Actually Work",
            "Why {keyword} Matters for Your Business",
            "The Future of {keyword}: Trends and Predictions"
        ]
    
    async def generate_ideas(self, keyword_groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate post ideas for each keyword group."""
        try:
            post_ideas = []
            
            for group in keyword_groups:
                group_ideas = self._generate_group_ideas(group)
                post_ideas.extend(group_ideas)
            
            logger.info(f"Generated {len(post_ideas)} post ideas")
            return post_ideas
            
        except Exception as e:
            logger.error(f"Error generating post ideas: {e}")
            return []
    
    def _generate_group_ideas(self, group: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate ideas for a specific keyword group."""
        keywords = group.get("keywords", [])
        group_name = group.get("name", "content")
        main_keyword = keywords[0] if keywords else group_name
        
        ideas = []
        
        # Generate different types of content ideas
        content_types = [
            {"type": "How-to Guide", "template": "How to {keyword}: Step-by-Step Guide"},
            {"type": "Listicle", "template": "10 Essential {keyword} Tips"},
            {"type": "Comparison", "template": "{keyword} vs Alternatives: Complete Comparison"},
            {"type": "Case Study", "template": "Real {keyword} Success Stories and Case Studies"},
            {"type": "Beginner Guide", "template": "{keyword} for Beginners: Getting Started"}
        ]
        
        for content_type in content_types:
            idea = {
                "id": f"idea_{group['id']}_{content_type['type'].lower().replace(' ', '_')}",
                "group_id": group["id"],
                "title": content_type["template"].format(keyword=main_keyword),
                "content_type": content_type["type"],
                "target_keywords": keywords[:3],  # Top 3 keywords
                "estimated_word_count": self._estimate_word_count(content_type["type"]),
                "difficulty": self._assess_difficulty(main_keyword),
                "description": self._generate_description(content_type["type"], main_keyword)
            }
            ideas.append(idea)
        
        return ideas
    
    def _estimate_word_count(self, content_type: str) -> int:
        """Estimate word count based on content type."""
        word_counts = {
            "How-to Guide": 1500,
            "Listicle": 1200,
            "Comparison": 2000,
            "Case Study": 1800,
            "Beginner Guide": 1600
        }
        return word_counts.get(content_type, 1500)
    
    def _assess_difficulty(self, keyword: str) -> str:
        """Assess content creation difficulty."""
        word_count = len(keyword.split())
        
        if word_count == 1:
            return "Hard"  # Broad topics are harder
        elif word_count == 2:
            return "Medium"
        else:
            return "Easy"  # Long-tail keywords are easier
    
    def _generate_description(self, content_type: str, keyword: str) -> str:
        """Generate content description."""
        descriptions = {
            "How-to Guide": f"A comprehensive step-by-step guide covering all aspects of {keyword}. Perfect for readers looking for actionable instructions.",
            "Listicle": f"An engaging list-format article highlighting the most important {keyword} tips and strategies.",
            "Comparison": f"An in-depth comparison analyzing {keyword} against alternatives, helping readers make informed decisions.",
            "Case Study": f"Real-world examples and success stories showcasing effective {keyword} implementation.",
            "Beginner Guide": f"A beginner-friendly introduction to {keyword}, covering fundamentals and getting started tips."
        }
        return descriptions.get(content_type, f"Comprehensive content about {keyword}.")
    
    def generate_social_media_ideas(self, keyword_groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate social media post ideas."""
        social_ideas = []
        
        for group in keyword_groups:
            main_keyword = group["keywords"][0] if group["keywords"] else group["name"]
            
            social_formats = [
                {
                    "platform": "LinkedIn",
                    "format": "Professional Tip",
                    "content": f"💡 Professional tip: Master {main_keyword} with these proven strategies...",
                    "hashtags": [f"#{main_keyword.replace(' ', '')}", "#productivity", "#business"]
                },
                {
                    "platform": "Twitter",
                    "format": "Quick Tip Thread",
                    "content": f"🧵 Thread: Everything you need to know about {main_keyword} (1/5)",
                    "hashtags": [f"#{main_keyword.replace(' ', '')}", "#tips", "#thread"]
                },
                {
                    "platform": "Instagram",
                    "format": "Carousel Post",
                    "content": f"Swipe to learn the top 5 {main_keyword} secrets →",
                    "hashtags": [f"#{main_keyword.replace(' ', '')}", "#education", "#tips"]
                }
            ]
            
            for social_format in social_formats:
                social_ideas.append({
                    "group_id": group["id"],
                    "platform": social_format["platform"],
                    "format": social_format["format"],
                    "content": social_format["content"],
                    "hashtags": social_format["hashtags"],
                    "target_keywords": [main_keyword]
                })
        
        return social_ideas
