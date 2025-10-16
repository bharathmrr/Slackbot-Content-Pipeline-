"""
Tests for keyword processor functionality.
"""

import pytest
from app.keyword.processor import KeywordProcessor


class TestKeywordProcessor:
    """Test cases for KeywordProcessor."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.processor = KeywordProcessor()
    
    def test_parse_comma_separated_keywords(self):
        """Test parsing comma-separated keywords."""
        text = "seo optimization, content marketing, digital strategy"
        keywords = self.processor.parse_keywords(text)
        
        assert len(keywords) == 3
        assert "seo optimization" in keywords
        assert "content marketing" in keywords
        assert "digital strategy" in keywords
    
    def test_parse_newline_separated_keywords(self):
        """Test parsing newline-separated keywords."""
        text = "seo optimization\ncontent marketing\ndigital strategy"
        keywords = self.processor.parse_keywords(text)
        
        assert len(keywords) == 3
        assert "seo optimization" in keywords
    
    def test_clean_keyword(self):
        """Test keyword cleaning."""
        dirty_keyword = "  SEO Optimization!!!  "
        clean_keyword = self.processor._clean_keyword(dirty_keyword)
        
        assert clean_keyword == "seo optimization"
    
    def test_is_valid_keyword(self):
        """Test keyword validation."""
        assert self.processor._is_valid_keyword("seo optimization") is True
        assert self.processor._is_valid_keyword("a") is False  # Too short
        assert self.processor._is_valid_keyword("123") is False  # Only numbers
        assert self.processor._is_valid_keyword("") is False  # Empty
    
    def test_deduplicate_keywords(self):
        """Test keyword deduplication."""
        keywords = ["seo", "SEO", "seo optimization", "seo"]
        deduplicated = self.processor.deduplicate_keywords(keywords)
        
        assert len(deduplicated) == 2  # "seo" and "seo optimization"
    
    @pytest.mark.asyncio
    async def test_parse_csv(self):
        """Test CSV parsing."""
        csv_content = "keyword\nseo optimization\ncontent marketing\ndigital strategy"
        keywords = await self.processor.parse_csv(csv_content)
        
        assert len(keywords) == 3
        assert "seo optimization" in keywords
    
    def test_get_keyword_stats(self):
        """Test keyword statistics."""
        keywords = ["seo", "content marketing", "digital strategy optimization"]
        stats = self.processor.get_keyword_stats(keywords)
        
        assert stats["total_count"] == 3
        assert stats["avg_length"] > 0
        assert stats["shortest"] == "seo"
        assert stats["longest"] == "digital strategy optimization"
