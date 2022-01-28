from search_service.indexer import FaissIndexer
from search_service.encoder import SbertEncoder

E = SbertEncoder()


def get_num_dimensions():

    embedding = E.encode(["test"])
    return embedding.shape[1]


def main():
    d = get_num_dimensions()
    I = FaissIndexer()

    # Load index if one already exists
    # I.load_index(file_name)
    # if I.index is None:
    # print("creating new index")
    # I.create_new_index(num_dimensions=d)

    # for document in documents:
    # E.encode()
    # I.add_to_index()

    # I.write_to_s3()


if __name__ == "__main__":
    main()
