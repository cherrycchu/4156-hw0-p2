"""Utilities related to searching and crawling documents for query"""
import json

import requests
import re

from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from nltk import WordNetLemmatizer


class ResultField:
    TITLE = "title"
    LINK = "link"
    SNIPPET = "snippet"
    PAGE_CONTENT = "page_content"
    MIME = "mime"
    FILE_FORMAT = "fileFormat"


SELECTED_FIELDS = [ResultField.TITLE, ResultField.LINK, ResultField.SNIPPET, ResultField.MIME, ResultField.FILE_FORMAT]
TEXT_FIELDS = [ResultField.TITLE, ResultField.LINK, ResultField.SNIPPET, ResultField.PAGE_CONTENT]

DOC_TAG_PATTERN = re.compile(r'<!--.*-->')


def get_top10(api_key, search_id, query) -> list:
    """Fetch top 10 Google Search Results from query.

    Data Structure:
        - results = [
            { title: value, link: value, snippet: value, page: value, other metadata: ... },
            { ... }
        ]
            - results is a list of result
            - result is a dictionary that maps a meaningful field (eg: title, link, snippet, page content, metadata) of
                a search to a value (text)
                - we'll be using the field values of a result to construct document vector for a document
                - TODO: need to differentiate html and nonhtml page ( inspect the result metadata ?)
                - TODO: additional scraping, we'll scrape the page content of a web page if necessary
    
    Args:
        api_key:
        search_id:
        query:

    Returns:

    """
    results = []
    resource = build("customsearch", "v1", developerKey=api_key, cache_discovery=False).cse()
    result = resource.list(q=query, cx=search_id).execute()

    for item in result['items']:
        result = {}

        # include only selected fields from result
        for field in SELECTED_FIELDS:
            result[field] = item.get(field, None)

        results.append(result)

    return results


def crawl_and_scrape_pages(results):
    """Crawl and scrape pages using requests + beautifulsoup4 if needed
    
    Arguments:
        results {[type]} -- [description]
    """
    for result in results:
        url = result["link"]
        content = ""

        if not is_result_a_file(result):
            content = scrape_page(url)

        # else:
        #     if result.get(ResultField.MIME) is not None and "pdf" in result[ResultField.MIME]:
        #         urlretrieve(url, "download.pdf")
        #         content = extract_text("download.pdf")

        result[ResultField.PAGE_CONTENT] = content

    return results


def scrape_page(url):
    response = requests.get(url)
    content = ""
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type')
        if isinstance(content_type, str) and 'text' in content_type:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "lxml")

            # kill all script and style elements
            for script in soup(["script", "style", "[document]", "head", "title"]):
                script.decompose()  # rip it out

            text = soup.get_text()

            # break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            content = text

    return content


def is_result_a_file(result):
    return result.get(ResultField.MIME) is not None or result.get(ResultField.FILE_FORMAT) is not None


# def visible(element):
#     if re.match('<!--.*-->', str(element.encode('utf-8'))):
#         return False
#     return True

#
# def clean_scraped_content(content=None):
#     """[summary]
#
#     TODO: clean scraped content with regex / pandas / etc
#
#     Arguments:
#         results {[type]} -- [description]
#     """
#     if content is None:
#         return ""
#
#     clean_content = content
#
#     # clean up html tags
#     if hasattr(content, "parent"):
#         x = list(filter(visible, content))
#         clean_content = list(filter(lambda a: a != '\n', x))
#
#     return " ".join(clean_content)
def normalize_word(word):
    lemmatizer = WordNetLemmatizer()
    return lemmatizer.lemmatize(word)