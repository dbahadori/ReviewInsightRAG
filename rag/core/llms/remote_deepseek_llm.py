from typing import List
import openai
from langchain_core.prompts import PromptTemplate
from rag.core.interfaces import ILLM, Document

class RemoteDeepSeekLLM(ILLM):
    def __init__(self, model_name: str = "deepseek-chat", api_key: str = None,
                 temperature: float = 0.3, max_tokens: int = 512, stream: bool = False):
        self.model_name = model_name
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Set the API base URL to DeepSeek's endpoint
        openai.api_base = "https://api.deepseek.com/v1"
        openai.api_key = self.api_key

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

        # Make a request to the DeepSeek API using OpenAI's ChatCompletion
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        # Extract and return the assistant's reply from the response
        return response.choices[0].message['content']
