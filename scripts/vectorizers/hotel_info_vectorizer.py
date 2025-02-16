from typing import List, Union
import numpy as np
from langchain.embeddings import HuggingFaceEmbeddings

class HotelInfoVectorizer:
    def __init__(self, embedding_model: str = "sentence-transformers/all-mpnet-base-v2"):
        self.model = HuggingFaceEmbeddings(model_name=embedding_model)

    def vectorize(self, data: Union[str, List[str]]) -> np.ndarray:
        """
        Converts hotel information (text) into vector embeddings.

        :param data: A single string or a list of strings to be vectorized.
        :return: A NumPy array of embeddings.
        """
        if isinstance(data, str):
            return np.array(self.model.embed_query(data))  # Single vector
        elif isinstance(data, list):
            return np.array(self.model.embed_documents(data))  # List of vectors
        else:
            raise ValueError("Input must be a string or a list of strings.")
