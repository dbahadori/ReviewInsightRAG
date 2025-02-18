from rag.core.llms.local_deepseek_llm import LocalDeepSeekLLM
from rag.core.llms.remote_deepseek_llm import RemoteDeepSeekLLM
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
        api_key = config.params.api_key
        mode = config.params.mode
        model = config.params.model
        temperature = config.params.temperature
        max_tokens = config.params.max_tokens
        stream = config.params.stream

        if provider == "deepseek":
            if mode == "remote":
                return RemoteDeepSeekLLM(model_name=model, api_key=api_key, temperature=temperature,
                                         max_tokens=max_tokens, stream=stream)
            elif mode == "local":
                return LocalDeepSeekLLM(model_name=model, temperature=temperature,
                                        max_tokens=max_tokens, stream=stream)
        elif provider == "openai":
            # Return an OpenAI LLM instance if needed.
            return RemoteDeepSeekLLM(model_name=model, api_key=api_key)  # For demonstration.
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
