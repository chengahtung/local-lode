"""
API Routes - FastAPI endpoint definitions
"""
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Generator
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ..models.schemas import (
    QueryRequest, QueryResponse,
    IngestRequest, IngestResponse,
    ConfigRequest, ConfigResponse,
    FileOperationRequest, FileOperationResponse,
    ResetResponse, FolderSelectionResponse
)
from ..services.rag_service import rag_service
from ..services.config_service import config_manager
from utils import file_utils

# Initialize logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["api"])


@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Execute a search query with optional reranking and LLM.
    """
    try:
        logger.info(f"Query request: {request.query[:50]}...")
        
        result = rag_service.query(
            query_text=request.query,
            use_rerank=request.use_rerank,
            use_llm=request.use_llm,
            n_results=request.n_results
        )
        
        return QueryResponse(**result)
    
    except Exception as e:
        logger.exception("Query endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query-stream")
async def query_stream_endpoint(request: QueryRequest):
    """
    Execute a search query with streaming results (SSE).
    """
    try:
        logger.info(f"Stream Query request: {request.query[:50]}...")
        
        generator = rag_service.query_stream(
            query_text=request.query,
            use_rerank=request.use_rerank,
            use_llm=request.use_llm,
            n_results=request.n_results
        )
        
        return StreamingResponse(
            generator, 
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    except Exception as e:
        logger.exception("Query stream endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest", response_model=IngestResponse)
async def ingest_endpoint(request: IngestRequest):
    """
    Ingest knowledge base files into ChromaDB.
    """
    try:
        logger.info(f"Ingest request: kb_folder={request.kb_folder}")
        
        count = rag_service.ingest_kb(
            kb_folder=request.kb_folder,
            chunk_size=request.chunk_size,
            overlap=request.overlap,
            batch_size=request.batch_size,
            ingest_docx=request.ingest_docx
        )
        
        return IngestResponse(
            success=True,
            chunks_upserted=count,
            message=f"Ingestion finished: {count} chunks upserted."
        )
    
    except Exception as e:
        logger.exception("Ingest endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset", response_model=ResetResponse)
async def reset_endpoint():
    """
    Reset ChromaDB collection by deleting all documents.
    """
    try:
        logger.info("Reset request received")
        
        count = rag_service.reset_collection()
        
        return ResetResponse(
            success=True,
            documents_removed=count,
            message=f"ChromaDB collection cleared. {count} documents removed."
        )
    
    except Exception as e:
        logger.exception("Reset endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config", response_model=ConfigResponse)
async def get_config_endpoint():
    """
    Get current configuration.
    """
    try:
        config = config_manager.get_all()
        
        return ConfigResponse(
            kb_folder=config.get("kb_folder", "kb"),
            chunk_size=config.get("chunk_size", 100000),
            overlap=config.get("overlap", 200),
            batch_size=config.get("batch_size", 64)
        )
    
    except Exception as e:
        logger.exception("Get config endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/config", response_model=ConfigResponse)
async def update_config_endpoint(request: ConfigRequest):
    """
    Update configuration.
    """
    try:
        logger.info("Update config request received")
        
        # Update only provided fields
        updates = {}
        if request.kb_folder is not None:
            updates["kb_folder"] = request.kb_folder
        if request.chunk_size is not None:
            updates["chunk_size"] = request.chunk_size
        if request.overlap is not None:
            updates["overlap"] = request.overlap
        if request.batch_size is not None:
            updates["batch_size"] = request.batch_size
        
        config_manager.update(updates)
        config = config_manager.get_all()
        
        return ConfigResponse(
            kb_folder=config.get("kb_folder", "kb"),
            chunk_size=config.get("chunk_size", 100000),
            overlap=config.get("overlap", 200),
            batch_size=config.get("batch_size", 64)
        )
    
    except Exception as e:
        logger.exception("Update config endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/open-file", response_model=FileOperationResponse)
async def open_file_endpoint(request: FileOperationRequest):
    """
    Open file in system default application.
    Uses existing file_utils.open_file function.
    """
    try:
        logger.info(f"Open file request: {request.path}")
        
        file_utils.open_file(request.path)
        
        return FileOperationResponse(
            success=True,
            message=f"Opened file: {request.path}"
        )
    
    except Exception as e:
        logger.exception("Open file endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/open-folder", response_model=FileOperationResponse)
async def open_folder_endpoint(request: FileOperationRequest):
    """
    Open folder in file explorer.
    Uses existing file_utils.open_folder function.
    """
    try:
        logger.info(f"Open folder request: {request.path}")
        
        file_utils.open_folder(request.path)
        
        return FileOperationResponse(
            success=True,
            message=f"Opened folder: {request.path}"
        )
    
    except Exception as e:
        logger.exception("Open folder endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/select-folder", response_model=FolderSelectionResponse)
async def select_folder_endpoint():
    """
    Open system folder selection dialog.
    """
    try:
        # Run in thread pool to avoid blocking async loop since tkinter might block
        path = await file_utils.run_in_thread(file_utils.select_folder_dialog)
        
        return FolderSelectionResponse(
            selected_folder=path,
            cancelled=path is None
        )
    except Exception as e:
        logger.exception("Select folder endpoint failed")
        # Fallback if threading fails or not available in file_utils yet
        try:
             path = file_utils.select_folder_dialog()
             return FolderSelectionResponse(
                selected_folder=path,
                cancelled=path is None
            )
        except Exception as inner_e:
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset-kb-folder", response_model=ConfigResponse)
async def reset_kb_folder_endpoint():
    """
    Reset KB folder to default.
    """
    try:
        config_manager.reset_to_default()
        config = config_manager.get_all()
        
        return ConfigResponse(
            kb_folder=config.get("kb_folder", "kb"),
            chunk_size=config.get("chunk_size", 100000),
            overlap=config.get("overlap", 200),
            batch_size=config.get("batch_size", 64)
        )
    except Exception as e:
        logger.exception("Reset KB folder endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))
