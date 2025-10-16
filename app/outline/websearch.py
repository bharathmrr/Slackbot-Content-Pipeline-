"""Web search API integration."""

import aiohttp
from typing import List, Dict, Any
from loguru import logger
from app.config import get_settings


class WebSearcher:
    """Handles web search API integration."""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def search_keywords(self, keywords: List[str], num_results: int = 10) -> List[Dict[str, Any]]:
        """Search for top-ranking content."""
        try:
            query = " ".join(keywords[:3])
            
            if self.settings.serp_api_key:
                return await self._search_with_serpapi(query, num_results)
            else:
                return self._generate_mock_results(keywords, num_results)
                
        except Exception as e:
            logger.error(f"Search error: {e}")
            return self._generate_mock_results(keywords, num_results)
    
    async def _search_with_serpapi(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Search using SerpAPI."""
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": self.settings.serp_api_key,
            "engine": "google",
            "num": num_results
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    for result in data.get("organic_results", []):
                        results.append({
                            "title": result.get("title", ""),
                            "url": result.get("link", ""),
                            "snippet": result.get("snippet", ""),
                            "position": result.get("position", 0)
                        })
                    return results
        return []
    
    def _generate_mock_results(self, keywords: List[str], num_results: int) -> List[Dict[str, Any]]:
        """Generate mock search results."""
        main_keyword = keywords[0] if keywords else "content"
        
        results = []
        for i in range(min(num_results, 5)):
            results.append({
                "title": f"Complete Guide to {main_keyword} - #{i+1}",
                "url": f"https://example{i+1}.com/guide-{main_keyword.replace(' ', '-')}",
                "snippet": f"Learn everything about {main_keyword} with this comprehensive guide.",
                "position": i + 1
            })
        
        return results
