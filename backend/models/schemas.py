"""
Pydantic models for request/response validation
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============= Query Models =============
class QueryRequest(BaseModel):
    query: str = Field(..., description="Search query text")
    use_rerank: bool = Field(default=True, description="Enable cross-encoder reranking")
    use_llm: bool = Field(default=False, description="Enable LLM-based answer generation")
    n_results: int = Field(default=10, description="Number of results to retrieve")


class DocumentResult(BaseModel):
    rank: int
    similarity: Optional[float]
    title: str
    source: str
    snippet: str
    document: str
    metadata: Dict[str, Any]


class QueryResponse(BaseModel):
    results: List[DocumentResult]
    llm_response: Optional[str] = None
    total_results: int


# ============= Ingest Models =============
class IngestRequest(BaseModel):
    kb_folder: str = Field(default="kb", description="Knowledge base folder path")
    chunk_size: int = Field(default=100000, description="Chunk size in characters")
    overlap: int = Field(default=200, description="Overlap size in characters")
    batch_size: int = Field(default=64, description="Batch size for upsert")
    ingest_docx: bool = Field(default=False, description="Include .docx files")


class IngestResponse(BaseModel):
    success: bool
    chunks_upserted: int
    message: str


# ============= Config Models =============
class ConfigRequest(BaseModel):
    kb_folder: Optional[str] = None
    chunk_size: Optional[int] = None
    overlap: Optional[int] = None
    batch_size: Optional[int] = None


class ConfigResponse(BaseModel):
    kb_folder: str
    chunk_size: int
    overlap: int
    batch_size: int


# ============= File Operation Models =============
class FileOperationRequest(BaseModel):
    path: str = Field(..., description="File or folder path to open")


class FileOperationResponse(BaseModel):
    success: bool
    message: str


# ============= Reset Models =============
class ResetResponse(BaseModel):
    success: bool
    documents_removed: int
    message: str


# ============= Folder Selection Models =============
class FolderSelectionResponse(BaseModel):
    selected_folder: Optional[str]
    cancelled: bool
