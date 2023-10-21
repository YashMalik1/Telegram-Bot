from collections import defaultdict
from libgen_api import LibgenSearch
import logging
import re
from collections import defaultdict

logging.basicConfig(level=logging.INFO)


def extract_page_count(page_str):
    """Extract the page count from a string. 
       E.g., "500 [219]" => 219, "219" => 219
    """
    match = re.search(r'\[(\d+)\]', page_str)
    if match:
        return int(match.group(1))
    return int(page_str)


def fetch_titles_from_libgen(title):
    """Fetch titles from Libgen based on the search title and filters."""
    search_instance = LibgenSearch()
    logging.info("Starting fetch...")
    title_filters = {"Extension": "pdf"}
    return search_instance.search_title_filtered(title, title_filters)


def extract_download_links(titles, search_instance):
    """Extract the download links for the given titles."""
    total_titles = len(titles)
    results = []

    for i, title in enumerate(titles):
        download_link = search_instance.resolve_download_links(title)
        url = download_link.get('IPFS.io', download_link.get('Cloudflare', download_link.get('GET', '')))
        if url != '':
            results.append({
                "title": title["Title"],
                "year": title["Year"],
                "pages": title["Pages"],
                "size": title["Size"],
                "url": url
                # Get the download link if available
            })
        logging.info(
            f"Download links {round(100 * i / total_titles, 2)}% fetched")

    return results

def semantic_score(query, text):
    """Compute a basic semantic score based on keyword matching."""
    query_keywords = set(query.lower().split())
    text_keywords = set(text.lower().split())
    common_keywords = query_keywords.intersection(text_keywords)
    return len(common_keywords)


def select_top_titles_for_resolution(titles, query, top_n=3):
    """Select a subset of titles based on semantic relevance."""
    title_scores = defaultdict(int)

    for title in titles:
        title_scores[title["Title"]] = semantic_score(query, title["Title"])

    # Sort titles by score and select the top N
    sorted_titles = sorted(
        titles, key=lambda x: title_scores[x["Title"]], reverse=True)
    return sorted_titles[:top_n]


def refine_results(results, query):
    """Refine the results to get the most relevant ones based on the criteria."""
    distinct_titles = {}

    for result in results:
        title_key = result["title"].lower()
        if title_key not in distinct_titles:
            distinct_titles[title_key] = []
        distinct_titles[title_key].append(result)

    refined_results = []
    for title_items in distinct_titles.values():
        if len(title_items) > 1:
            title_items.sort(key=lambda x: (
                x["year"],
                x["size"],
                -extract_page_count(x["pages"])
            ))

            for item in title_items:
                if "Mb" not in item["size"] or int(item["size"][0:-2]) < 48:
                    refined_results.append(item)
                    break
            else:
                refined_results.append(title_items[0])
        else:
            refined_results.append(title_items[0])

    return refined_results


def libgenBook(title, resolution_count=3):
    """Main function to search for a book on Libgen and refine the results."""
    titles = fetch_titles_from_libgen(title)
    logging.info("Titles fetched")

    # Select a subset of titles for resolution
    top_titles = select_top_titles_for_resolution(
        titles, title, top_n=resolution_count)
    results = extract_download_links(top_titles, LibgenSearch())
    logging.info("Download links fetched")

    return refine_results(results, title)
