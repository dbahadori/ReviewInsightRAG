from typing import List

from rag.core.interfaces import ILLM, Document


class OpenAI(ILLM):
    def __init__(self, api_key: str, model: str = ""):
        pass
    def generate(self, query: str, context: List[Document]) -> str:
        pass

        # for chunk in api_client.chat_completion(prompt='Hi', stream=True):
        #     print(chunk, end='', flush=True)