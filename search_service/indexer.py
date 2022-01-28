from abc import ABC, abstractmethod
import faiss
from search_service.s3_helpers import download_file_from_s3, upload_file_to_s3, load_env_var
import faiss
import os

FILE_NAME = load_env_var("EMBEDDING_PATH")
BUCKET_NAME = load_env_var("BUCKET_NAME")


class Indexer(ABC):

    def __init__(self, index_path: str):
        self.index_path = index_path
        self.index = self.load_index()

    @abstractmethod
    def load_index(self):
        pass

    @abstractmethod
    def add_to_index(self, query: str):
        pass

    @abstractmethod
    def search(self, top_k: int = 5):
        pass

    @abstractmethod
    def write_to_s3(self):
        pass


class FaissIndexer(Indexer):

    def load_index(self):
        """
        Try to load index from file. If not, download from S3.
        """
        print("Loading index from path {}...".format(FILE_NAME))
        if os.path.exists(FILE_NAME):
            print("{} exists. Loading...".format(FILE_NAME))
            response = faiss.read_index(FILE_NAME)
            print("Loaded index with {} entries from disk.".format(response.ntotal))
            return response

        print("File does not exist. Will download...")
        if download_file_from_s3(FILE_NAME, BUCKET_NAME, FILE_NAME):
            print("Downloading index from s3")
            response = faiss.read_index(FILE_NAME)
            print("Loaded index with {} entries from.".format(response.ntotal))
            return response
        else:
            raise FileNotFoundError(
                "Could not find index at {}. Please make new index first.".format(FILE_NAME))

    def add_to_index(self, vector: str):
        next_id = self.index.ntotal
        self.index.add_with_ids(vector, [next_id])

        # Update db with new index

    def search(self, vector, top_k: int = 5):
        print("Searching for closest...")
        # D = distance matrix
        # I = index matrix
        # Each row of the matrix = query
        # Each column = distance or index of closest match. 1st column = closest
        D, I = self.index.search(vector, top_k)

        closest_ids = []

        for query_result in I:
            for result_id in query_result:
                closest_ids.append(int(result_id))
        return list(closest_ids)

    def write_to_s3(self):
        faiss.write_index(self.index, FILE_NAME)
        upload_file_to_s3(FILE_NAME, BUCKET_NAME)
