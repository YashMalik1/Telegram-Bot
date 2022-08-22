import os
import requests
from dotenv import load_dotenv
from collections import defaultdict
import re


# Custom Error Classes for clarity


class InvalidTitleLengthError(Exception):
    pass


class InvalidTitleTypeError(Exception):
    pass


# Load environment variables
load_dotenv()

# Global configurations
SUBSCRIPTION_KEY = os.environ['BING_SEARCH_V7_SUBSCRIPTION_KEY']
ENDPOINT = os.environ['BING_SEARCH_V7_ENDPOINT'] + "/v7.0/search"


def validate_title(title):
    """
    Validates the title based on length and type.

    Args:
        title (string): The name of the book

    Returns:
        title (string): Validated title

    Raises:
        InvalidTitleLengthError: If title length is not within valid range
        InvalidTitleTypeError: If title is not a string
    """
    if not isinstance(title, str):
        raise InvalidTitleTypeError("Title should be a string.")

    title_length = len(title)
    if title_length < 3:
        raise InvalidTitleLengthError("Title is too short.")
    elif title_length > 70:
        raise InvalidTitleLengthError("Title is too long.")

    return title


def fetch_from_bing(query, count=50):
    """
    Fetches data from Bing based on the query.

    Args:
        query (string): The search query
        count (int): Number of results to fetch

    Returns:
        list: List of dictionaries containing title and URL

    Raises:
        Exception: If any error occurs during API call
    """
    headers = {'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY}
    params = {
        'q': query,
        'mkt': 'en-US',
        "responseFilter": "webPages",
        "count": str(count)
    }

    response = requests.get(ENDPOINT, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()
    return [{"title": link["name"], "url": link["url"]} for link in data["webPages"]["value"]]


def compute_score(keyword, title, url):
    """
    Compute a score for a result based on the presence of the keyword in the title and URL.

    Args:
        keyword (str): The keyword to search for
        title (str): The title of the search result
        url (str): The URL of the search result

    Returns:
        int: The score of the result
    """
    # Count occurrences of the keyword (case-insensitive)
    title_score = len(re.findall(keyword, title, flags=re.IGNORECASE))
    url_score = len(re.findall(keyword, url, flags=re.IGNORECASE))

    # Consider the length of the title (shorter titles might be more relevant)
    length_penalty = 1 / (len(title) + 1)

    return (title_score + url_score) * length_penalty


def rank_results(keyword, results):
    """
    Rank the search results based on their relevance to the keyword.

    Args:
        keyword (str): The keyword to rank results for
        results (list): List of dictionaries containing title and URL

    Returns:
        list: Sorted list of results based on their relevance
    """
    scores = defaultdict(int)
    for result in results:
        scores[result["url"]] = compute_score(
            keyword, result["title"], result["url"])

    # Sort results based on score
    sorted_results = sorted(
        results, key=lambda x: scores[x["url"]], reverse=True)
    return sorted_results


def bingoBook(title, count=50):
    """
    Searches for a book on Bing and ranks the results for relevance.

    Args:
        title (str): The name of the book
        count (int): Number of results to fetch

    Returns:
        list: List of dictionaries containing title and URL ranked based on their relevance

    Raises:
        Exception: If any error occurs during the process
    """
    title = validate_title(title)
    query = f"{title} filetype:pdf"
    results = fetch_from_bing(query, count)
    return rank_results(title, results)


# Test the function
if __name__ == "__main__":
    try:
        results = bingo_book("Harry Potter")
        for result in results:
            print(result)
    except Exception as e:
        print(f"Error: {e}")
