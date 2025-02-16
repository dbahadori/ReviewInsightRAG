from rag.core.llms.deepSeekLLM import DeepSeekLLM
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
        provider = config.get("provider", "deepseek").lower()
        api_key = config.get("api_key")
        model = config.get("model", "deepseek-r1:14b")
        if provider == "deepseek":
            return DeepSeekLLM(model_name=model, api_key=api_key)
        elif provider == "openai":
            # Return an OpenAI LLM instance if needed.
            return DeepSeekLLM(model_name=model, api_key=api_key)  # For demonstration.
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
