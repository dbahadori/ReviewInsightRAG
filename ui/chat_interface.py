from rag.core.processor import QueryProcessor


class ChatInterface:
    def __init__(self, query_processor: QueryProcessor):
        self.query_processor = query_processor

    def submitQuery(self, query: str) -> str:
        return self.query_processor.process(query)

    def displayResponse(self, response: str):
        print(f"Response: {response}")
