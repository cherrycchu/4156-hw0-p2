import os
from urllib.request import urlretrieve

import lxml
import nltk
import pytest
import requests
from bs4 import BeautifulSoup
from lxml.html.clean import Cleaner
from pdfminer.high_level import extract_text

from fetchq import FetchQ
from search_utils import get_top10, crawl_and_scrape_pages


@pytest.fixture
def api_key():
    return os.getenv("SEARCH_API_KEY")

@pytest.fixture
def search_id():
    return os.getenv("SEARCH_ID")


def test_get10(api_key, search_id):
    pass
    # query = "information retrieval ppt"
    # results = get_top10(api_key=api_key, search_id=search_id, query=query)
    # results = crawl_and_scrape_pages(results)
    # print(results)


def test_get10_with_pdf(api_key, search_id):
    query = "rocchio algorithm"
    results = get_top10(api_key=api_key, search_id=search_id, query=query)
    results = crawl_and_scrape_pages(results)
    print(results)


def test_get_pdf():
    url = "https://www.cs.cornell.edu/people/tj/publications/joachims_97a.pdf"
    response = requests.get(url)
    content_type = response.headers['Content-Type']
    if "pdf" in content_type:
        urlretrieve(url, "download.pdf")
        content = extract_text("download.pdf")
        print(content)


def test_scrape_page():
    url = "https://en.wikipedia.org/wiki/Rocchio_algorithm"
    response = requests.get(url)
    soup = BeautifulSoup(response.text)

    # kill all script and style elements
    for script in soup.body(["script", "style", '[document]', 'head', 'title']):
        script.decompose()  # rip it out

    text = soup.body.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    print(text)

    # cleaner = Cleaner()
    # cleaner.javascript = True  # This is True because we want to activate the javascript filter
    # cleaner.style = True  # This is True because we want to activate the style
    # print(lxml.html.tostring(cleaner.clean_html(lxml.html.parse('http://www.google.com'))))
# def test_fetchtop_10():
#     # with pdf results
#
#     precision = 0.9
#
#     fetchq = FetchQ(api_key, search_id, query, precision, use_stopwords=True, scrape_results=False)
#     results = fetchq.fetch_top10(query)
#     print(results)
#     # query = "conditional random field"