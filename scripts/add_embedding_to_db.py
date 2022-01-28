from search_service.indexer import FaissIndexer
from search_service.encoder import SbertEncoder
import numpy as np
from pymongo.collection import Collection
from database.mongodb import prod_database as db

E = SbertEncoder()


def add_encoding_to_db(collection: Collection, text_column_name: str, embedding_column_name: str = "embedding"):

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
            "$set": {"embedding": embedding.tolist()}
        }
        collection.update_one({"_id": _id}, update_details)
        i += 1

    print("Finished adding encodings.")


if __name__ == "__main__":
    add_encoding_to_db(collection=db.blurb, text_column_name="text")
