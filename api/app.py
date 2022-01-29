from operator import index
from typing import List
from fastapi import FastAPI
from search_service.encoder import SbertEncoder
from search_service.indexer import FaissIndexer
from search_service.s3_helpers import load_env_var
from database.mongodb import prod_database as db
from bson.objectid import ObjectId

FILE_NAME = load_env_var("EMBEDDING_PATH")

app = FastAPI()
E = SbertEncoder()
F = FaissIndexer()
F.load_index()


@app.get("/")
def read_root():
    return "Encoder"


@app.get("/search")
def get_results(q: str):
    if q:
        embedding = E.encode([q])
        result = F.search(embedding)
        payload = get_restaurant_results_payload(result)
        return payload
    else:
        return "Need query"

# TODO: Refactor + clean up


def get_restaurant_results_payload(index_ids: List[int]):
    result = []

    # Get all blurbs with index ids
    _index_id_filter = {
        "embedding_index_id": {"$in": index_ids}
    }

    blurbs = db.blurb.find(_index_id_filter)

    # Store unique restaurants. Some restaurants may have more than 1 blurb.
    restaurant_ids = set()

    # Get blurbs + articles about a restaurant and add to payload
    for blurb in blurbs:
        restaurant_id: ObjectId = blurb["restaurant_id"]

        # Skip blurb if restaurant already exists
        if restaurant_id in restaurant_ids:
            continue

        restaurant = db.restaurant.find_one({"_id": restaurant_id})
        # Skip blurb is restaurant cannot be found
        if not restaurant:
            continue

        # Get blurbs for the restaurant
        restaurant_blurbs = db.blurb.find(
            {"restaurant_id": restaurant_id})

        article_payload = {}

        # Get the text + article ID for all the blurbs about a restaurant
        article_ids = []
        blurb_texts = {}
        for blurb in restaurant_blurbs:
            article_id = blurb["article_id"]
            article_ids.append(article_id)
            blurb_texts[str(article_id)] = blurb["text"]

        # Get articles for the restaurant
        articles = db.article.find({"_id": {"$in": article_ids}})
        article_payload = [
            {
                "_id": str(article["_id"]),
                "title": article["title"],
                "url": article["url"],
                "text": blurb_texts[str(article["_id"])]
            } for article in articles]

        # Add payload
        result.append({
            "_id": str(restaurant["_id"]),
            "name": restaurant["name"],
            "articles": article_payload
        })
        restaurant_ids.add(restaurant_id)
    return result
