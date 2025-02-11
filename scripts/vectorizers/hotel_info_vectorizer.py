from langchain_community.embeddings import HuggingFaceEmbeddings


class HotelInfoVectorizer:
    def __init__(self, embedding_model: str = "sentence-transformers/all-mpnet-base-v2"):
        self.model = HuggingFaceEmbeddings(model_name=embedding_model)

    def vectorize(self, data):
        return {key: self.model.embed_text(value) for key, value in data.items()}
