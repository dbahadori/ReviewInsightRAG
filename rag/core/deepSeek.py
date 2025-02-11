from typing import List
from deepseek import DeepSeekAPI  # Hypothetical DeepSeek SDK
from rag.core.interfaces import ILLM, Document

class DeepSeek(ILLM):
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        self.client = DeepSeekAPI(api_key)

    def generate(self, query: str, context: List[Document]) -> str:
        context_str = "\n".join([doc.content for doc in context])
        prompt = f"Context: {context_str}\n\nQuestion: {query}\nAnswer:"
        return self.client.chat_completion(prompt=prompt, stream=False)
