"""
Semantic clustering and grouping of keywords using vector search.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from loguru import logger

from app.config import get_settings


class KeywordGrouper:
    """Groups keywords using semantic similarity and clustering."""
    
    def __init__(self):
        self.settings = get_settings()
        self.model: Optional[SentenceTransformer] = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the sentence transformer model."""
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Sentence transformer model loaded")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None
    
    async def group_keywords(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Group keywords using semantic clustering."""
        try:
            if not keywords or len(keywords) < 2:
                return [{"id": "group_1", "name": keywords[0] if keywords else "empty", "keywords": keywords, "score": 1.0}]
            
            embeddings = await self._generate_embeddings(keywords)
            if embeddings is None:
                return self._fallback_grouping(keywords)
            
            groups = self._cluster_keywords(keywords, embeddings)
            logger.info(f"Grouped {len(keywords)} keywords into {len(groups)} clusters")
            return groups
            
        except Exception as e:
            logger.error(f"Error grouping keywords: {e}")
            return self._fallback_grouping(keywords)
    
    async def _generate_embeddings(self, keywords: List[str]) -> Optional[np.ndarray]:
        """Generate embeddings for keywords."""
        try:
            if not self.model:
                return None
            embeddings = self.model.encode(keywords, convert_to_tensor=False)
            return np.array(embeddings)
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return None
    
    def _cluster_keywords(self, keywords: List[str], embeddings: np.ndarray) -> List[Dict[str, Any]]:
        """Cluster keywords based on embeddings."""
        try:
            n_clusters = min(self.settings.max_groups_per_batch, max(1, len(keywords) // 3))
            
            if n_clusters <= 1:
                return [{"id": "group_1", "name": self._generate_group_name(keywords), "keywords": keywords, "score": 1.0}]
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(embeddings)
            
            groups = []
            for cluster_id in range(n_clusters):
                cluster_keywords = [keywords[i] for i in range(len(keywords)) if cluster_labels[i] == cluster_id]
                if cluster_keywords:
                    groups.append({
                        "id": f"group_{cluster_id + 1}",
                        "name": self._generate_group_name(cluster_keywords),
                        "keywords": cluster_keywords,
                        "score": 0.8
                    })
            
            return groups
            
        except Exception as e:
            logger.error(f"Error clustering: {e}")
            return self._fallback_grouping(keywords)
    
    def _generate_group_name(self, keywords: List[str]) -> str:
        """Generate a name for a keyword group."""
        if not keywords:
            return "Empty Group"
        if len(keywords) == 1:
            return keywords[0]
        
        # Find common words
        word_freq = {}
        for keyword in keywords:
            for word in keyword.split():
                if len(word) > 2:
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get most common word
        if word_freq:
            common_word = max(word_freq, key=word_freq.get)
            return f"{common_word} related"
        
        return f"{keywords[0]} group"
    
    def _fallback_grouping(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Fallback grouping when clustering fails."""
        if not keywords:
            return []
        
        group_size = max(3, len(keywords) // 5)
        groups = []
        
        for i in range(0, len(keywords), group_size):
            group_keywords = keywords[i:i + group_size]
            groups.append({
                "id": f"group_{len(groups) + 1}",
                "name": self._generate_group_name(group_keywords),
                "keywords": group_keywords,
                "score": 0.5
            })
        
        return groups
