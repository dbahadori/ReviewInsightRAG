from rag.core.interfaces import IQueryProcess


class ChatInterface:
    def __init__(self, query_processor: IQueryProcess):
        self.query_processor = query_processor

    def submit_query(self, query: str) -> str:
        return self.query_processor.process(query)

    def display_response(self, response: str):
        print(f"Response: {response}")
