# take payload and filter

from typing import Any, List


def filter_by_categories(payload: List["dict[str, Any]"], categories: str):
    """
    `categories` is the string of categories from the HTTP request's query parameter.
    """
    if categories:
        categories_to_include = set(categories.split(","))

        def filter_categories(entry):
            for category in entry["categories"]:
                if category in categories_to_include:
                    return True
            return False

        return list(filter(filter_categories, payload))
    else:
        return payload


def filter_by_articles(payload: List["dict[str, Any]"], articles: str):
    """
    `articles` is the string of articles from the HTTP request's query parameter.
    """

    if articles:
        articles_to_include = set(articles.split(","))

        def filter_articles(entry):
            for article in entry["articles"]:
                if article["_id"] in articles_to_include:
                    return True
            return False
        return list(filter(filter_articles, payload))
    else:
        return payload


def filter_by_price(payload: List["dict[str, Any]"], price: str):

    if price:
        prices_to_include = set(price.split(","))

        def filter_prices(entry):
            if entry["price"] in prices_to_include:
                return True
            return False
        return list(filter(filter_prices, payload))
    else:
        return payload


def filter_results(payload: List["dict[str, Any]"], filters: " dict[str, Any]"):
    result = payload
    for key in filters:
        if key == "categories":
            result = filter_by_categories(
                payload=result, categories=filters[key])
        elif key == "articles":
            result = filter_by_articles(payload=result, articles=filters[key])
        elif key == "price":
            result = filter_by_price(payload=result, price=filters[key])
        else:
            raise ValueError("{} is not a valid filter.".format(key))

    return result
