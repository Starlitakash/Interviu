from typing import List, Dict, Any, Optional
from app.retrieval.curriculum_indexer import CurriculumIndexer

def retrieve_curriculum_context(
    indexer: CurriculumIndexer,
    topic: str,
    day: Optional[str] = None,
    top_k: int = 3
) -> str:
    """Retrieve formatted curriculum text snippet for a given topic and day."""
    if not indexer:
        return "No curriculum indexed."
        
    query = f"{topic} {day if day else ''}"
    results = indexer.search(query=query, day_filter=day, top_k=top_k)
    
    context_blocks = []
    for idx, chunk in enumerate(results, 1):
        context_blocks.append(f"--- Chunk {idx} ({chunk['metadata']['day']} - {chunk['metadata']['topic']}) ---\n{chunk['text']}")
        
    return "\n\n".join(context_blocks)
