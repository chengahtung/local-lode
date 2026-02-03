"""
RAG Service - Handles all RAG operations (query, ingest, rerank)
Wraps existing rag_utils functions without modifying them.
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator
import sys

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from utils import rag_utils as ru
from .chroma_service import chroma_manager
from .config_service import config_manager


class RAGService:
    """
    RAG Service class that wraps existing rag_utils functions.
    Provides OOP interface for RAG operations without modifying rag_utils.py.
    """
    
    def __init__(self):
        """Initialize RAG service"""
        self.logger = logging.getLogger(__name__)
        self.chroma_manager = chroma_manager
        self.config_manager = config_manager
    
    def query(
        self,
        query_text: str,
        use_rerank: bool = True,
        use_llm: bool = False,
        n_results: int = 10
    ) -> Dict[str, Any]:
        """
        Execute a search query with optional reranking and LLM.
        
        Args:
            query_text: Search query string
            use_rerank: Whether to use cross-encoder reranking
            use_llm: Whether to use LLM for answer generation
            n_results: Number of results to retrieve
        
        Returns:
            Dictionary containing results and optional LLM response
        """
        try:
            self.logger.info(f"Querying: {query_text[:50]}...")
            
            # Query ChromaDB using existing rag_utils function
            collection = self.chroma_manager.get_collection()
            results = collection.query(
                query_texts=query_text,
                n_results=n_results,
                where={"type": {"$in": ["md", "txt", "docx"]}},
                include=["documents", "metadatas", "distances"],
            )
            
            # Transform results using existing rag_utils function
            top_records = ru.transform_result(results)
            
            # Rerank if requested
            rerank_top_records = []
            if use_rerank and top_records:
                self.logger.info("Re-ranking results...")
                reranker_keep_loaded = self.config_manager.get("reranker_keep_loaded", True)
                rerank_pairs = ru.rerank_with_cross_encoder_v2(
                    query_text,
                    top_records,
                    stay_active=reranker_keep_loaded
                )
                rerank_top_records = [rec for rec, score in rerank_pairs]
            
            # Choose which records to use
            chosen_records = rerank_top_records if rerank_top_records else top_records or []
            
            # Format results for response
            formatted_results = []
            for i, rec in enumerate(chosen_records, start=1):
                doc = rec.get("document", "") or ""
                meta = rec.get("metadata", {}) or {}
                
                # Calculate similarity
                sim = rec.get("similarity", None)
                if sim is None:
                    score = rec.get("score", None)
                    if isinstance(score, (int, float)) and 0.0 <= score <= 1.0:
                        sim = 1.0 - float(score)
                
                # Create snippet
                snippet = (" ".join(doc.split()))[:140]
                if len(" ".join(doc.split())) > 140:
                    snippet = snippet.rstrip() + "..."
                
                entry = {
                    "rank": i,
                    "similarity": float(sim) if sim is not None else None,
                    "title": meta.get("title") or Path(meta.get("source_file", "")).stem,
                    "source": meta.get("source_file") or meta.get("source") or "",
                    "snippet": snippet,
                    "document": doc,
                    "metadata": meta,
                }
                formatted_results.append(entry)
            
            # Call LLM if requested
            llm_response = None
            if use_llm and chosen_records:
                self.logger.info("Calling LLM...")
                try:
                    # Use existing rag_utils function with streaming to ensure we can consume the generator
                    llm_gen = ru.call_llm(
                        question=query_text,
                        top_records=chosen_records[:10],
                        stream=True
                    )
                    # Consume the generator to get the full string
                    llm_response = "".join([chunk for chunk in llm_gen])
                except Exception as e:
                    self.logger.exception("LLM call failed")
                    llm_response = f"(LLM call failed: {e})"
            
            return {
                "results": formatted_results,
                "llm_response": llm_response,
                "total_results": len(formatted_results)
            }
        
        except Exception as e:
            self.logger.exception("Query failed")
            raise e
        
    def query_stream(
        self,
        query_text: str,
        use_rerank: bool = True,
        use_llm: bool = False,
        n_results: int = 10
    ) -> Generator[str, None, None]:
        """
        Execute a search query and stream results (SSE format).
        Yields:
            JSON strings formatted as SSE data:
            data: {"type": "results", "payload": {...}}\n\n
            data: {"type": "chunk", "payload": "..."}\n\n
        """
        import json
        try:
            self.logger.info(f"Streaming Query: {query_text[:50]}...")
            
            # 1. Reuse existing query function logic (partially) or call it?
            # Calling self.query with use_llm=False to get results first is cleaner
            # assuming query() separates retrieval and LLM.
            # But query() does unrelated LLM logic if use_llm is True.
            # So let's call query() with use_llm=False to get documents.
            
            base_result = self.query(
                query_text=query_text,
                use_rerank=use_rerank,
                use_llm=False,  # Don't run LLM yet
                n_results=n_results
            )
            
            # Yield results event
            yield f"data: {json.dumps({'type': 'results', 'payload': base_result})}\n\n"
            
            if use_llm and base_result["results"]:
                self.logger.info("Streaming LLM...")
                
                # Re-construct chosen_records from the base_result
                # base_result["results"] is a list of formatted dicts.
                # rag_utils.call_llm needs the original record structure or at least dicts with 'document', 'title', 'id'.
                # Fortunately our formatted_results contain 'document', 'title' and 'metadata'.
                # We can map them back to what call_llm likely needs.
                
                # Check rag_utils.call_llm expectation:
                # context = "\n\n".join(f"[{r.get('id')}], Title: [{r.get('title')}]\n {r.get('document')}" for r in top_records)
                # Our formatted 'results' have 'title', 'document'. 'id' is inside 'metadata' likely, or we can use 'rank'.
                # Let's see formatted_entry in query():
                # entry = { ... "document": doc, "metadata": meta ... }
                # meta has "id".
                
                # We can pass the formatted results directly if they have the keys.
                # formatted_results has 'title', 'document'. It might miss 'id' at top level, but let's check.
                # query() does: "title": meta.get("title")...
                # call_llm uses r.get('id'), r.get('title'), r.get('document').
                
                # We need to adapt base_result["results"] slightly or just ensure keys exist.
                llm_records = []
                for res in base_result["results"]:
                    # Create a dict that satisfies call_llm
                    llm_records.append({
                        "id": res["metadata"].get("id", str(res["rank"])),
                        "title": res["title"],
                        "document": res["document"]
                    })
                    
                # Call LLM with stream=True
                llm_gen = ru.call_llm(
                    question=query_text,
                    top_records=llm_records[:10],
                    stream=True
                )
                
                for chunk in llm_gen:
                    # Yield token event
                    # chunk is string
                    # Use json.dumps to handle newlines/quotes safely
                    yield f"data: {json.dumps({'type': 'chunk', 'payload': chunk})}\n\n"
            
            # Yield done event
            yield f"data: {json.dumps({'type': 'done', 'payload': None})}\n\n"
            
        except Exception as e:
            self.logger.exception("Stream query failed")
            yield f"data: {json.dumps({'type': 'error', 'payload': str(e)})}\n\n"

    def ingest_kb(
        self,
        kb_folder: str = "kb",
        chunk_size: int = 100000,
        overlap: int = 200,
        batch_size: int = 64,
        ingest_docx: bool = False
    ) -> int:
        """
        Ingest knowledge base files into ChromaDB.
        Uses existing rag_utils.ingest_kb_to_collection function.
        
        Args:
            kb_folder: Path to knowledge base folder
            chunk_size: Chunk size in characters
            overlap: Overlap size in characters
            batch_size: Batch size for upsert
            ingest_docx: Whether to include .docx files
        
        Returns:
            Number of chunks upserted
        """
        try:
            self.logger.info(f"Starting ingestion from {kb_folder}...")
            
            # Get paths
            project_root = Path(__file__).resolve().parent.parent.parent
            kb_path = project_root / kb_folder if kb_folder == "kb" else Path(kb_folder)
            kb_path.mkdir(exist_ok=True)
            
            # Use existing rag_utils function
            collection = self.chroma_manager.get_collection()
            count = ru.ingest_kb_to_collection(
                app_dir=project_root,
                kb_dir=kb_path,
                ingest_docx_flag=ingest_docx,
                collection=collection,
                chunk_size=chunk_size,
                overlap=overlap,
                batch_size=batch_size,
                file_globs=["**/*.md", "**/*.txt"],
            )
            
            self.logger.info(f"Ingestion finished: {count} chunks upserted.")
            return count
        
        except Exception as e:
            self.logger.exception("Ingestion failed")
            raise e
    
    def reset_collection(self) -> int:
        """
        Reset ChromaDB collection by deleting all documents.
        
        Returns:
            Number of documents removed
        """
        try:
            self.logger.info("Resetting collection...")
            count = self.chroma_manager.reset_collection()
            return count
        except Exception as e:
            self.logger.exception("Reset failed")
            raise e


# Singleton instance
rag_service = RAGService()
