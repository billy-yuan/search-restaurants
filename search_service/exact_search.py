from cgitb import text
from typing import Any, List
from pymongo.collection import Collection
from database.mongodb import prod_database as db


class ExactSearch:
    def __init__(self, collection: Collection):
        self.collection = collection

    def search(self, text_query: str, min_score: float = 3) -> List["dict[str, Any]"]:
        stage_match_text = {
            '$search': {
                'index': 'text',
                'text': {
                    'query': text_query,
                    'path': {
                        'wildcard': '*'
                    }
                }
            }
        }

        stage_get_score = {
            "$addFields": {
                "text_match_score": {
                    "$meta": "searchScore"
                }
            }
        }

        stage_filter_score = {
            "$match": {
                "text_match_score": {
                    "$gte": min_score
                }
            }
        }

        _filter = [stage_match_text, stage_get_score, stage_filter_score]

        cursor = self.collection.aggregate(_filter)
        results = []

        for item in cursor:
            results.append(item)

        return results
