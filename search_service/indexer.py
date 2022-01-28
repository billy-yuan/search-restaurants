from abc import ABC, abstractmethod
import faiss
from search_service.s3_helpers import download_file_from_s3, upload_file_to_s3, load_env_var
import faiss
import os

FILE_NAME = load_env_var("EMBEDDING_PATH")  # name of file on disk
BUCKET_NAME = load_env_var("BUCKET_NAME")
# name of s3 object. Same as file name by default
S3_OBJECT_NAME = load_env_var("EMBEDDING_PATH")


class Indexer(ABC):

    @abstractmethod
    def load_index(self):
        pass

    @abstractmethod
    def add_to_index(self, query: str):
        pass

    @abstractmethod
    def search(self, vector, top_k: int = 5):
        pass

    @abstractmethod
    def write_to_s3(self):
        """
        Write current index to s3
        """
        pass

    @abstractmethod
    def create_new_index(self):
        """
        Create a new index and set `self.index` to the new index.
        """
        pass


class FaissIndexer(Indexer):
    def load_index(self,
                   file_name: str = FILE_NAME,
                   bucket_name: str = BUCKET_NAME) -> None:
        """
        Try to load index from file. If not, download from S3.
        """
        print("Loading index from path {}...".format(file_name))
        if os.path.exists(file_name):
            print("{} exists. Loading...".format(file_name))
            response = faiss.read_index(file_name)
            print("Loaded index with {} entries from disk.".format(response.ntotal))
            self.index = response

        print("File does not exist. Will download...")
        if download_file_from_s3(file_name, bucket_name, s3_object_name=file_name):
            print("Downloading index from s3")
            response = faiss.read_index(file_name)
            print("Loaded index with {} entries from.".format(response.ntotal))
            self.index = response
        else:
            raise FileNotFoundError(
                "Could not find index at {}. Please make new index first.".format(file_name))

    def add_to_index(self, vector):
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

    def write_to_s3(self, file_name=FILE_NAME, bucket_name=BUCKET_NAME):
        print("Write index to file")
        faiss.write_index(self.index, file_name)
        print("Write index to s3")
        upload_file_to_s3(file_name, bucket_name)

    def create_new_index(self, num_dimensions: int, index_path: str = FILE_NAME):
        print("Creating new index")
        index = faiss.IndexFlatL2(num_dimensions)
        index = faiss.IndexIDMap(index)

        self.index = index
        print("New index created and set to self.index")
