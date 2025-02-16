from pydantic import BaseModel
from typing import Optional

# Retriever settings
class RetrieverParams(BaseModel):
    embedding_model: str
    device: str

class RetrieverSettings(BaseModel):
    framework: str
    params: RetrieverParams

# Document store settings
class DocumentStoreParams(BaseModel):
    persistent: bool
    index_path: str
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

class LLMSettings(BaseModel):
    provider: str
    params: LLMParams

# Scraper settings
class ScraperParams(BaseModel):
    api_key: str

class ScraperSettings(BaseModel):
    type: str
    params: ScraperParams

# Main settings class
class Settings(BaseModel):
    retriever: RetrieverSettings
    document_store: DocumentStoreSettings
    llm: LLMSettings
    scraper: ScraperSettings
