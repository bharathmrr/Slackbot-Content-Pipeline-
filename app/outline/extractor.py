"""
Content extraction from web pages.
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from loguru import logger


class ContentExtractor:
    """Extracts headings and meta info from web pages."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def extract_from_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Extract content from multiple URLs."""
        tasks = []
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            headers=self.headers
        ) as session:
            for url in urls:
                tasks.append(self._extract_single_url(session, url))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions
            valid_results = []
            for result in results:
                if isinstance(result, dict):
                    valid_results.append(result)
                else:
                    logger.warning(f"Failed to extract from URL: {result}")
            
            return valid_results
    
    async def _extract_single_url(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        """Extract content from a single URL."""
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return {"url": url, "error": f"HTTP {response.status}"}
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                return {
                    "url": url,
                    "title": self._extract_title(soup),
                    "headings": self._extract_headings(soup),
                    "meta_description": self._extract_meta_description(soup),
                    "word_count": self._estimate_word_count(soup),
                    "content_structure": self._analyze_structure(soup)
                }
                
        except Exception as e:
            logger.error(f"Error extracting from {url}: {e}")
            return {"url": url, "error": str(e)}
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return "No title found"
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all headings with hierarchy."""
        headings = []
        
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text = tag.get_text().strip()
            if text and len(text) > 3:  # Filter out very short headings
                headings.append({
                    "level": int(tag.name[1]),
                    "text": text,
                    "tag": tag.name
                })
        
        return headings
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description."""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc.get('content').strip()
        
        # Fallback to first paragraph
        first_p = soup.find('p')
        if first_p:
            text = first_p.get_text().strip()
            return text[:160] + "..." if len(text) > 160 else text
        
        return "No description found"
    
    def _estimate_word_count(self, soup: BeautifulSoup) -> int:
        """Estimate word count of the page."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        words = text.split()
        return len(words)
    
    def _analyze_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze content structure."""
        structure = {
            "h1_count": len(soup.find_all('h1')),
            "h2_count": len(soup.find_all('h2')),
            "h3_count": len(soup.find_all('h3')),
            "paragraph_count": len(soup.find_all('p')),
            "list_count": len(soup.find_all(['ul', 'ol'])),
            "image_count": len(soup.find_all('img')),
            "link_count": len(soup.find_all('a'))
        }
        
        return structure
    
    def create_content_outline(self, extracted_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a content outline from extracted data."""
        if not extracted_data:
            return {"error": "No data to analyze"}
        
        # Aggregate all headings
        all_headings = []
        for data in extracted_data:
            if "headings" in data:
                all_headings.extend(data["headings"])
        
        # Group headings by level
        heading_groups = {}
        for heading in all_headings:
            level = heading["level"]
            if level not in heading_groups:
                heading_groups[level] = []
            heading_groups[level].append(heading["text"])
        
        # Find common patterns
        common_h2s = self._find_common_headings(heading_groups.get(2, []))
        common_h3s = self._find_common_headings(heading_groups.get(3, []))
        
        return {
            "total_pages_analyzed": len(extracted_data),
            "common_h2_headings": common_h2s[:10],  # Top 10
            "common_h3_headings": common_h3s[:10],  # Top 10
            "heading_distribution": {
                level: len(headings) for level, headings in heading_groups.items()
            },
            "suggested_outline": self._generate_suggested_outline(common_h2s, common_h3s)
        }
    
    def _find_common_headings(self, headings: List[str]) -> List[str]:
        """Find common heading patterns."""
        if not headings:
            return []
        
        # Simple frequency count
        heading_count = {}
        for heading in headings:
            # Normalize heading
            normalized = heading.lower().strip()
            heading_count[normalized] = heading_count.get(normalized, 0) + 1
        
        # Sort by frequency
        sorted_headings = sorted(heading_count.items(), key=lambda x: x[1], reverse=True)
        
        # Return headings that appear more than once
        return [heading for heading, count in sorted_headings if count > 1]
    
    def _generate_suggested_outline(self, common_h2s: List[str], common_h3s: List[str]) -> List[Dict[str, Any]]:
        """Generate a suggested content outline."""
        outline = []
        
        # Introduction
        outline.append({
            "level": 2,
            "heading": "Introduction",
            "description": "Overview and introduction to the topic"
        })
        
        # Add common H2 headings
        for heading in common_h2s[:5]:  # Top 5
            outline.append({
                "level": 2,
                "heading": heading.title(),
                "description": f"Section covering {heading.lower()}"
            })
        
        # Add some H3 subheadings under the last H2
        if common_h3s and len(outline) > 1:
            for heading in common_h3s[:3]:  # Top 3
                outline.append({
                    "level": 3,
                    "heading": heading.title(),
                    "description": f"Subsection about {heading.lower()}"
                })
        
        # Conclusion
        outline.append({
            "level": 2,
            "heading": "Conclusion",
            "description": "Summary and final thoughts"
        })
        
        return outline
