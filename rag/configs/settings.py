from pydantic import BaseModel
from typing import Optional

# Retriever settings
class RetrieverParams(BaseModel):
    embedding_model: str
    device: str

class RetrieverSettings(BaseModel):
    framework: str
    params: RetrieverParams
    document_store: 'DocumentStoreSettings'  # Nested document store settings

# Document store settings
class DocumentStoreParams(BaseModel):
    persistent: bool
    index_path: Optional[str] = None
    embedding_model: str
    api_key: Optional[str] = None  # Only needed for Pinecone
    index_name: Optional[str] = None  # Only needed for Pinecone

class DocumentStoreSettings(BaseModel):
    type: str
    params: DocumentStoreParams

# LLM settings
class LLMParams(BaseModel):
    api_key: str
    model: str
    mode: str
    temperature: float
    max_tokens: int
    stream: bool

class LLMSettings(BaseModel):
    provider: str
    params: LLMParams

# Scraper settings
class ScraperParams(BaseModel):
    api_key: str

class ScraperSettings(BaseModel):
    type: str
    params: ScraperParams

# Hash store settings
class HashStoreParams(BaseModel):
    db_path: str

class HashStoreSettings(BaseModel):
    type: str
    params: HashStoreParams

# Main settings class
class Settings(BaseModel):
    retriever: RetrieverSettings
    llm: LLMSettings
    scraper: ScraperSettings
    hash_store: HashStoreSettings
