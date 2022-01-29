from search_service.encoder import SbertEncoder
from search_service.s3_helpers import load_env_var
import faiss
import numpy as np


FILE_NAME = load_env_var("EMBEDDING_PATH")
BUCKET_NAME = load_env_var("BUCKET_NAME")


def test_search():
    """
    Test to see FAISS search works with our encoder.
    """
    encoder = SbertEncoder()
    data = [
        'What color is chameleon?',
        'When is the festival of colors?',
        'When is the next music festival?',
        'How far is the moon?',
        'How far is the sun?',
        'What happens when the sun goes down?',
        'What we do in the shadows?',
        'What is the meaning of all this?',
        'What is the meaning of Russel\'s paradox?',
        'How are you doing?'
    ]
    encoded_data = encoder.encode(data)
    num_dimensions = encoded_data[0].shape[0]

    # Make index
    index = faiss.IndexFlatIP(num_dimensions)
    index.add(encoded_data)

    # Add new data
    new_data = "Omelettes are the best for breakfast"
    data.append(new_data)
    new_encoded_data = encoder.encode([new_data])
    print(new_encoded_data)
    index.add(new_encoded_data)

    def search(query: str, top_k):
        query_vector = encoder.encode([query])

        # D = distance matrix
        # I = index matrix
        # Each row of the matrix = query
        # Each column = distance or index of closest match. 1st column = closest
        D, I = index.search(query_vector, top_k)
        print("Query: {}".format(query))
        print(I)
        for result in I:
            for i in result:
                print("Closest match:", data[i])

    search("moon", 1)
    search("breakfast", 1)
    search("shadow", 1)


def make_test_index(num_rows: int = 100000, d: int = 384):
    """
    Make a test index. 
    `num_rows` is the number of vectors.
    `d` is the number of dimensions in the vector.
    """
    print("Testing by calling the function test()")
    np.random.seed(1234)             # make reproducible
    xb = np.random.random((num_rows, d)).astype('float32')

    index = faiss.IndexFlatL2(d)   # build the index
    index = faiss.IndexIDMap(index)
    ids = np.array(range(0, xb.shape[0]))
    index.add_with_ids(xb, ids)

    xq = np.random.random((1, d)).astype('float32')

    print("Writing index to {}".format(FILE_NAME))
    faiss.write_index(index, FILE_NAME)
