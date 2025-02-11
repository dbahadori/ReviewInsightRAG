from rag.core.deepSeek import DeepSeek
from rag.core.openAI import OpenAI
from rag.core.interfaces import ILLM

class LLMFactory:
    @staticmethod
    def create_llm(config: dict) -> ILLM:
        """
        Creates an LLM instance based on the provided configuration.

        Args:
            config (dict): Configuration for the LLM (e.g., provider, API key, model).

        Returns:
            ILLM: An instance of the requested LLM provider.
        """
        provider = config.get("provider", "deepseek")  # Default to DeepSeek
        api_key = config.get("api_key")
        model = config.get("model", "deepseek-chat")  # Default model

        if provider == "deepseek":
            return DeepSeek(api_key=api_key, model=model)
        elif provider == "openai":
            return OpenAI(api_key=api_key, model=model)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
