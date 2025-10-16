"""
Keyword processing for CSV/text parsing, cleaning & normalization.
"""

import csv
import io
import re
from typing import List, Set
from loguru import logger


class KeywordProcessor:
    """Handles keyword parsing, cleaning, and normalization."""
    
    def __init__(self):
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with'
        }
    
    def parse_keywords(self, text: str) -> List[str]:
        """Parse keywords from text input."""
        try:
            # Split by common delimiters
            delimiters = [',', '\n', ';', '\t']
            keywords = [text]
            
            for delimiter in delimiters:
                new_keywords = []
                for keyword in keywords:
                    new_keywords.extend(keyword.split(delimiter))
                keywords = new_keywords
            
            # Clean and filter keywords
            cleaned_keywords = []
            for keyword in keywords:
                cleaned = self._clean_keyword(keyword.strip())
                if cleaned and self._is_valid_keyword(cleaned):
                    cleaned_keywords.append(cleaned)
            
            # Remove duplicates while preserving order
            return list(dict.fromkeys(cleaned_keywords))
            
        except Exception as e:
            logger.error(f"Error parsing keywords from text: {e}")
            return []
    
    async def parse_csv(self, csv_content: str) -> List[str]:
        """Parse keywords from CSV content."""
        try:
            keywords = []
            csv_file = io.StringIO(csv_content)
            
            # Try to detect if there's a header
            sniffer = csv.Sniffer()
            sample = csv_content[:1024]
            has_header = sniffer.has_header(sample)
            
            csv_file.seek(0)
            reader = csv.reader(csv_file)
            
            # Skip header if present
            if has_header:
                next(reader, None)
            
            for row in reader:
                if not row:
                    continue
                
                # Try different column strategies
                keyword = self._extract_keyword_from_row(row)
                if keyword:
                    cleaned = self._clean_keyword(keyword)
                    if cleaned and self._is_valid_keyword(cleaned):
                        keywords.append(cleaned)
            
            # Remove duplicates
            return list(dict.fromkeys(keywords))
            
        except Exception as e:
            logger.error(f"Error parsing CSV: {e}")
            return []
    
    def _extract_keyword_from_row(self, row: List[str]) -> str:
        """Extract keyword from CSV row."""
        if not row:
            return ""
        
        # If only one column, use it
        if len(row) == 1:
            return row[0].strip()
        
        # Look for the most likely keyword column
        for cell in row:
            cell = cell.strip()
            if cell and len(cell) > 1 and not cell.isdigit():
                return cell
        
        # Fallback to first non-empty cell
        for cell in row:
            if cell.strip():
                return cell.strip()
        
        return ""
    
    def _clean_keyword(self, keyword: str) -> str:
        """Clean and normalize a keyword."""
        if not keyword:
            return ""
        
        # Convert to lowercase
        keyword = keyword.lower().strip()
        
        # Remove extra whitespace
        keyword = re.sub(r'\s+', ' ', keyword)
        
        # Remove special characters except hyphens and spaces
        keyword = re.sub(r'[^\w\s-]', '', keyword)
        
        # Remove leading/trailing hyphens
        keyword = keyword.strip('-')
        
        return keyword.strip()
    
    def _is_valid_keyword(self, keyword: str) -> bool:
        """Check if a keyword is valid."""
        if not keyword:
            return False
        
        # Length checks
        if len(keyword) < 2 or len(keyword) > 100:
            return False
        
        # Must contain at least one letter
        if not re.search(r'[a-zA-Z]', keyword):
            return False
        
        # Skip if it's just numbers
        if keyword.isdigit():
            return False
        
        # Skip if it's just a stop word
        if keyword in self.stop_words:
            return False
        
        # Skip if it's just punctuation
        if re.match(r'^[^\w\s]+$', keyword):
            return False
        
        return True
    
    def deduplicate_keywords(self, keywords: List[str]) -> List[str]:
        """Remove duplicate keywords using various strategies."""
        if not keywords:
            return []
        
        # Simple deduplication
        seen = set()
        deduplicated = []
        
        for keyword in keywords:
            # Normalize for comparison
            normalized = keyword.lower().strip()
            
            if normalized not in seen:
                seen.add(normalized)
                deduplicated.append(keyword)
        
        return deduplicated
    
    def filter_similar_keywords(self, keywords: List[str], threshold: float = 0.8) -> List[str]:
        """Filter out very similar keywords."""
        if not keywords:
            return []
        
        filtered = []
        
        for keyword in keywords:
            is_similar = False
            
            for existing in filtered:
                if self._calculate_similarity(keyword, existing) > threshold:
                    # Keep the shorter one
                    if len(keyword) < len(existing):
                        filtered.remove(existing)
                        filtered.append(keyword)
                    is_similar = True
                    break
            
            if not is_similar:
                filtered.append(keyword)
        
        return filtered
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using Jaccard similarity."""
        if not str1 or not str2:
            return 0.0
        
        # Convert to sets of words
        words1 = set(str1.lower().split())
        words2 = set(str2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def get_keyword_stats(self, keywords: List[str]) -> dict:
        """Get statistics about the keywords."""
        if not keywords:
            return {
                "total_count": 0,
                "avg_length": 0,
                "avg_words": 0,
                "shortest": "",
                "longest": "",
                "word_count_distribution": {}
            }
        
        lengths = [len(k) for k in keywords]
        word_counts = [len(k.split()) for k in keywords]
        
        # Word count distribution
        word_dist = {}
        for count in word_counts:
            word_dist[count] = word_dist.get(count, 0) + 1
        
        return {
            "total_count": len(keywords),
            "avg_length": sum(lengths) / len(lengths),
            "avg_words": sum(word_counts) / len(word_counts),
            "shortest": min(keywords, key=len),
            "longest": max(keywords, key=len),
            "word_count_distribution": word_dist
        }
