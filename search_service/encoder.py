from base64 import encode
from multiprocessing.sharedctypes import Value
from typing import Any, List
from numpy import ndarray
from sentence_transformers import SentenceTransformer
import numpy.typing as npt


class SbertEncoder:
    """
    Wrapper for Sentence Transformer.
    """
    model = SentenceTransformer(
        model_name_or_path="multi-qa-MiniLM-L6-cos-v1")

    @classmethod
    def encode(cls, text: List[str], show_progress_bar: bool = False) -> ndarray:
        """
        Encodes a list of strings into a numpy array of embeddings.
        """

        result = cls.model.encode(sentences=text,
                                  show_progress_bar=show_progress_bar,
                                  convert_to_numpy=True,
                                  normalize_embeddings=True)

        if type(result).__name__ == "ndarray":
            return result  # type: ignore
        else:
            raise ValueError("Encoding is not of type ndarray")
