from typing import List, Dict, Any
from app.retrieval.chunker import chunk_curriculum
from app.utils.logger import logger

class CurriculumIndexer:
    """In-memory indexer for session curriculum chunks."""
    
    def __init__(self, curriculum: Dict[str, Any]):
        self.curriculum = curriculum
        self.chunks = chunk_curriculum(curriculum)
        logger.info(f"Indexed {len(self.chunks)} curriculum topic chunks.")

    def search(self, query: str, day_filter: str = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search curriculum chunks matching query and optional day filter.
        """
        query_words = set(query.lower().split())
        scored_chunks = []
        
        for chunk in self.chunks:
            # Metadata filter
            if day_filter:
                chunk_day = str(chunk["metadata"]["day"]).lower()
                target_day = str(day_filter).lower()
                if target_day not in chunk_day and chunk_day not in target_day:
                    continue
                    
            chunk_words = set(chunk["text"].lower().split())
            overlap = len(query_words & chunk_words)
            scored_chunks.append((overlap, chunk))
            
        # Sort by overlap score descending
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        results = [item[1] for item in scored_chunks[:top_k]]
        if not results and self.chunks:
            # Fallback if filter returned empty
            return self.chunks[:top_k]
            
        return results
