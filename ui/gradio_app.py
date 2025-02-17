import gradio as gr

from rag.core.interfaces import IRetriever, ILLM
from rag.core.processors.main_query_process import MainQueryProcess
from ui.chat_interface import ChatInterface


# Assume you have already built your container and loaded the document store.
def create_chat_interface(hotel_retriever: IRetriever, review_retriever: IRetriever, llm: ILLM) -> ChatInterface:
    # Build a simple query processor.
    qp = MainQueryProcess(hotel_retriever, review_retriever, llm)
    return ChatInterface(qp)


def launch_gradio_ui(hotel_retriever: IRetriever, review_retriever: IRetriever, llm: ILLM):
    chat_interface = create_chat_interface(hotel_retriever, review_retriever, llm)

    def respond(query):
        return chat_interface.submit_query(query)

    with gr.Blocks() as demo:
        gr.Markdown("# RAG System Chat Interface")
        query_input = gr.Textbox(label="Enter your query")
        output = gr.Textbox(label="Response")
        query_input.submit(fn=respond, inputs=query_input, outputs=output)
    demo.launch()
