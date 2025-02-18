from typing import List
import openai
from langchain_core.prompts import PromptTemplate
from rag.core.interfaces import ILLM, Document
import requests

class LocalDeepSeekLLM(ILLM):
    def __init__(self, model_name: str = "deepseek-chat",
                 temperature: float = 0.3, max_tokens: int = 512, stream: bool=False):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stream = stream

        # Set the API base URL to DeepSeek's endpoint
        self.base_add = "http://127.0.0.1:11434/api/generate"

        # Define a prompt template for generating answers
        self.prompt_template = PromptTemplate.from_template(
            """
            Answer the user's query based on the provided context.

            Context:
            {context}

            Query:
            {query}

            Answer in Persian:
            """
        )

    def generate(self, query: str, context: List[Document]) -> str:
        # Combine all document texts into a single context string
        combined_context = "\n\n".join([doc.content for doc in context])
        prompt = self.prompt_template.format(context=combined_context, query=query)

        # Prepare the payload
        payload = {
            "model": self.model_name,  # Model name
            "prompt": prompt,  # User input
            "stream": self.stream,  # Set to True for streaming responses
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        # Send the request to Ollama
        response = requests.post(self.base_add, json=payload)

        # Extract and return the assistant's reply from the response
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response
            result = response.json()
            return result["response"]
        else:
            return f"Error: {response.status_code} - {response.text}"
