from typing import List
from sentence_transformers import SentenceTransformer


class SbertEncoder:
    """
    Wrapper for Sentence Transformer.
    """
    model = SentenceTransformer(
        model_name_or_path="multi-qa-MiniLM-L6-cos-v1")

    @classmethod
    def encode(cls, text: List[str], convert_to_tensor: bool = False):
        """
        Encodes a list of strings into a numpy array of embeddings.
        """

        return cls.model.encode(sentences=text,
                                show_progress_bar=True,
                                convert_to_numpy=True,
                                convert_to_tensor=convert_to_tensor,
                                normalize_embeddings=True)
