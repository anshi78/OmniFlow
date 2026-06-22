"""Vector Store Service for disruption case history and RAG memory search."""

import logging
import random
from typing import Dict, Any, List, Optional
import numpy as np

logger = logging.getLogger("omniflow.vector_store")

# In-memory document storage fallback
_in_memory_docs: List[Dict[str, Any]] = []

class VectorStoreService:
    """Provides semantic search capabilities for historical disruption playbook resolution."""

    def __init__(self):
        # We can implement a simplified semantic search using mock vectors or TF-IDF
        logger.info("🧠 Initialized pgvector memory store (using in-memory fallback)")

    def _get_mock_embedding(self, text: str) -> np.ndarray:
        """Generates a pseudo-deterministic mock embedding for query matching."""
        # Standard seed based on characters in text
        char_sum = sum(ord(c) for c in text.lower())
        random.seed(char_sum)
        vec = np.array([random.uniform(-1, 1) for _ in range(128)])
        # Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    async def add_document(self, text: str, metadata: Dict[str, Any]):
        """Adds a document/playbook to vector store memory."""
        embedding = self._get_mock_embedding(text)
        _in_memory_docs.append({
            "text": text,
            "metadata": metadata,
            "embedding": embedding
        })
        logger.debug(f"Added document to vector store: {text[:50]}...")

    async def similarity_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Searches historical case studies/resolutions using cosine similarity."""
        if not _in_memory_docs:
            # Seed some default playbook responses if empty
            await self._seed_default_playbooks()

        query_emb = self._get_mock_embedding(query)
        scored_docs = []
        
        for doc in _in_memory_docs:
            cos_sim = float(np.dot(query_emb, doc["embedding"]))
            scored_docs.append((cos_sim, doc))

        # Sort by similarity score descending
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, doc in scored_docs[:k]:
            results.append({
                "text": doc["text"],
                "metadata": doc["metadata"],
                "score": score
            })
            
        return results

    async def _seed_default_playbooks(self):
        """Pre-populate the vector store with realistic supply chain playbooks."""
        playbooks = [
            (
                "Supplier bankrupt or offline due to strike. Strategy: Contact back-up supplier immediately, split order 60/40 between near-shore options, expedite shipment with premium shipping, and re-allocate warehouse reserves.",
                {"scenario": "supplier_strike", "resolution_speed": "high", "cost_increase": "medium"}
            ),
            (
                "Regional demand spike or viral trend. Strategy: Shift inventory from non-spike regions to spike locations, request local store-to-store transfers, increase warehouse order batch frequency, and apply daily order limits.",
                {"scenario": "demand_spike", "resolution_speed": "instant", "cost_increase": "low"}
            ),
            (
                "Warehouse shutdown or equipment failure. Strategy: Route incoming vendor shipments directly to other operational centers (cross-docking), shift order processing logic to neighboring warehouses, and notify regional carriers of rerouted pick-up points.",
                {"scenario": "warehouse_shutdown", "resolution_speed": "medium", "cost_increase": "high"}
            ),
            (
                "Severe blizzard or storm blocking transport routes. Strategy: Ground all shipping routes in red alert areas, reroute trucks through southern corridors, notify stores of a 48-hour ETA delay, and trigger automatic safety stock buffer increase.",
                {"scenario": "weather_disaster", "resolution_speed": "high", "cost_increase": "medium"}
            )
        ]
        
        for text, meta in playbooks:
            await self.add_document(text, meta)

# Global vector store instance
vector_store = VectorStoreService()
