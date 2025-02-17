from rag.core.llms.deepSeekLLM import DeepSeekLLM
from rag.core.interfaces import ILLM

class LLMFactory:
    @staticmethod
    def create_llm(config) -> ILLM:
        """
        Creates an LLM instance based on the provided configuration.

        Args:
            config : Configuration for the LLM (e.g., provider, API key, model).

        Returns:
            ILLM: An instance of the requested LLM provider.
        """
        provider = config.provider.lower()
        api_key = config.api_key
        model = config.model
        if provider == "deepseek":
            return DeepSeekLLM(model_name=model, api_key=api_key)
        elif provider == "openai":
            # Return an OpenAI LLM instance if needed.
            return DeepSeekLLM(model_name=model, api_key=api_key)  # For demonstration.
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
