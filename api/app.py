from typing import Any, List
from fastapi import FastAPI, HTTPException
from search_service.encoder import SbertEncoder
from search_service.indexer import FaissIndexer
from search_service.s3_helpers import load_env_var
from database.mongodb import prod_database as db
from bson.objectid import ObjectId
from search_service.exact_search import ExactSearch
from fastapi.middleware.cors import CORSMiddleware

FILE_NAME = load_env_var("EMBEDDING_PATH")
origins = [
    "http://localhost:3000"
]
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

E = SbertEncoder()
F = FaissIndexer()
F.load_index()

min_scores = {
    "restaurant": float(load_env_var("EXACT_SEARCH_MIN_SCORE_RESTAURANT")),
    "article": float(load_env_var("EXACT_SEARCH_MIN_SCORE_ARTICLE")),
    "blurb": float(load_env_var("EXACT_SEARCH_MIN_SCORE_BLURB"))
}


@app.get("/")
def read_root():
    return "Encoder"


@app.get("/search")
def get_results(q: str):
    if q:
        exact_search_results = get_exact_search_results(q)
        semantic_search_results = get_semantic_search_results(q)

        # Dedupe + combine search results
        combined_results = exact_search_results + semantic_search_results
        deduped_results = {}

        for result in combined_results:
            _id = str(result["_id"])
            if _id not in deduped_results:
                deduped_results[_id] = result

        payload = []

        for _id in deduped_results:
            payload.append(deduped_results[_id])
        return payload

    else:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")


def get_restaurant_address(restaurant: "dict[str, Any]") -> str:
    if restaurant["location"] and "display_address" in restaurant["location"]:
        return restaurant["location"]["display_address"]
    else:
        return restaurant["address"]


# TODO: Refactor + clean up
def get_restaurant_payload_from_blurbs(_filter: "dict[str, Any]") -> "List[dict[str, Any]]":
    result = []

    # Get all blurbs
    blurbs = db.blurb.find(_filter)

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

        # Skip restaurant if restaurant is closed
        if restaurant["is_closed"] == True:
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
            "address": get_restaurant_address(restaurant),
            "price": restaurant["price"],
            "categories": restaurant["categories"] if "categories" in restaurant else [],
            "coordinates": restaurant["coordinates"],
            "articles": article_payload
        })
        restaurant_ids.add(restaurant_id)
    return result


def get_semantic_search_results(q: str):
    embedding = E.encode([q])
    index_ids = F.search(embedding)
    _index_id_filter = {
        "embedding_index_id": {"$in": index_ids}
    }
    return get_restaurant_payload_from_blurbs(_index_id_filter)


def get_exact_search_results(q: str) -> "List[dict[str, Any]]":
    article_exact_search = ExactSearch(db.article)
    restaurant_exact_search = ExactSearch(db.restaurant)
    blurb_exact_search = ExactSearch(db.blurb)

    # Articles
    articles = article_exact_search.search(q, min_scores["article"])
    article_filter = {
        "article_id": {"$in": [article["_id"] for article in articles]}}
    article_payload = get_restaurant_payload_from_blurbs(article_filter)

    # Restaurants
    restaurants = restaurant_exact_search.search(q, min_scores["restaurant"])
    restaurant_filter = {
        "restaurant_id": {"$in": [restaurant["_id"] for restaurant in restaurants]}
    }

    restaurant_payload = get_restaurant_payload_from_blurbs(
        restaurant_filter)

    # Blurbs
    blurbs = blurb_exact_search.search(q, min_scores["blurb"])
    blurb_filter = {
        "_id": {"$in": [blurb["_id"] for blurb in blurbs]}
    }
    blurb_payload = get_restaurant_payload_from_blurbs(blurb_filter)
    # Make payload

    combined_payload = restaurant_payload + article_payload + blurb_payload
    payload = {str(item["_id"]): item for item in combined_payload}

    result = []
    for _ in payload:
        result.append(payload[_])

    return result
