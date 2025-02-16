import gradio as gr

from rag.core.factories.retriever_factory import RetrieverFactory
from rag.core.interfaces import DocumentType
from rag.core.processors.main_query_process import MainQueryProcess
from rag.core.processors.processor import QueryProcessor
from rag.core.retrievers.combined_retriever import CombinedRetriever
from rag.data.faiss_store import FAISSStore
from ui.chat_interface import ChatInterface
from rag.core.factories.llm_factory import LLMFactory


# Assume you have already built your container and loaded the document store.
def create_chat_interface(retriever_config: dict, llm_config: dict) -> ChatInterface:
    # Build a simple query processor.
    qp = MainQueryProcess(retriever_config, llm_config)
    return ChatInterface(qp)


def launch_gradio_ui(retriever_config: dict, llm_config: dict):
    chat_interface = create_chat_interface(retriever_config, llm_config)

    def respond(query):
        return chat_interface.submit_query(query)

    with gr.Blocks() as demo:
        gr.Markdown("# RAG System Chat Interface")
        query_input = gr.Textbox(label="Enter your query")
        output = gr.Textbox(label="Response")
        query_input.submit(fn=respond, inputs=query_input, outputs=output)
    demo.launch()
