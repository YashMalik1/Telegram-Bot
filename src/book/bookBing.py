import json
import os
from pprint import pprint
import requests
from dotenv import load_dotenv
load_dotenv()
from errors import ValueTooSmallError, ValueTooLargeError

# Add your Bing Search V7 subscription key and endpoint to your environment variables.
subscription_key = os.environ['BING_SEARCH_V7_SUBSCRIPTION_KEY']
endpoint = os.environ['BING_SEARCH_V7_ENDPOINT'] + "/v7.0/search"

def bingoBook(title, count= 50):
    """
    Calls the bing api to find top search results corresponding to the query

    Args:
        title (string): The name of the book
        count (integer): The number of results you want to get

    Raises:
        ex: Server Error 500
    """

    if(type(title) is not str):
        title = str(title)
    elif(len(title) < 3):
        raise ValueTooSmallError
    elif(len(title) > 70):
        raise ValueTooLargeError
    

    # Query term(s) to search for.
    query = f"{title} filetype:pdf"

    # Construct a request
    mkt = 'en-US'
    responseFilter = "webPages"
    count = str(count)
    params = {'q': query, 'mkt': mkt, "responseFilter": responseFilter, "count": count}
    headers = {'Ocp-Apim-Subscription-Key': subscription_key}

    # Call the API
    try:
        print("Calling bing... ")

        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        result = []
        for link in data["webPages"]["value"]:
            result.append({
                "title": link["name"],
                "url": link["url"],
            })

        return result
    except Exception as ex:
        raise ex
