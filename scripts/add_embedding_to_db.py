from turtle import update
from search_service.indexer import FaissIndexer
from search_service.encoder import SbertEncoder
import numpy as np
from pymongo.collection import Collection
from database.mongodb import prod_database as db

# Get the number of dimensions by running a test string through the encoder
E = SbertEncoder()
num_dimensions = E.encode(["test"]).shape[1]


def add_embedding_to_db(collection: Collection, text_column_name: str, embedding_column_name: str = "embedding"):
    """
    Encode the records in a MongoDB collection.
    `text_column_name`: Name of the column that contains the text to be encoded.
    `embedding_column_name`: Name of the column that will contain the encoding.
    """
    records = collection.find({embedding_column_name: {"$eq": None}})

    print("Adding encodings...")
    i = 1
    for record in records:
        # Print status every 10
        if i % 10 == 0:
            print("{} completed".format(i))

        # Make embedding
        embedding = E.encode(record[text_column_name])

        # Update record
        _id = record["_id"]
        update_details = {
            "$set": {embedding_column_name: embedding.tolist()}
        }
        collection.update_one({"_id": _id}, update_details)
        i += 1

    print("Finished adding encodings.")


def add_index_to_db(collection: Collection,
                    embedding_index_id_column_name: str = "embedding_index_id",
                    embedding_column_name: str = "embedding"):
    """
    Add index ID to mongodb so that the MongoDB collection can be mapped to the FAISS index.

    `embedding_index_id_column_name`: name of the mongodb field for the embedding index id (i.e. FAISS id)
    `embedding`: name of the mongodb field that has the embedding.
    """
    print("Adding index to db")

    I = FaissIndexer()
    # Load index if one already exists, otherwise create a new index
    I.load_index()

    if I.index is None:
        I.create_new_index(num_dimensions=num_dimensions)
    if I.index is None:
        raise ValueError("No index found.")

    # Get all records without an encoding
    records = collection.find({embedding_index_id_column_name: {"$eq": None}})

    # Get the latest index id
    index_id: int = I.get_next_id()
    print("Starting indexid", index_id)

    i = 1
    for record in records:
        _id = record["_id"]

        # Get the embedding from the document
        embedding = np.array(
            [record[embedding_column_name]]).astype(np.float32)

        # Add embedding to index
        I.add_to_index(embedding)

        # Add index ID to the document
        update_details = {
            "$set": {embedding_index_id_column_name: index_id}
        }
        collection.update_one({"_id": _id}, update_details)

        # Print every 10 records
        if i % 10 == 0:
            print("{} documents added to index".format(i))

        index_id += 1
        i += 1
    I.write_to_s3()

    if i > 1:
        print("Finished adding indexes.")
    else:
        print("No documents needed to be embedded.")


if __name__ == "__main__":
    add_embedding_to_db(collection=db.blurb, text_column_name="text")
    add_index_to_db(collection=db.blurb)
