"""Orchestrates of the whole query expansion pipeline from query to query expansion iterations"""
import re

import nltk

from config import GAMMA, BETA, ALPHA
from ir_utils import transform_results_to_vector_space_model, rocchio_model, get_stopwords

from search_utils import get_top10, ResultField, crawl_and_scrape_pages, TEXT_FIELDS

INIT_MSG = """~=~=~ Welcome to FetchQ, we'll fetch documents for your query! ~=~=~"""
SEARCH_MSG = """Your Parameters:
===
API Key             = {api_key}
Search ID           = {search_id}
Query               = {query}
Target Precision    = {precision}
"""
SUMMARY_MSG = """FEEDBACK SUMMARY
===
Query       = {query}
Precision   = {user_precision}"""

OPTIONS_PATTERN = re.compile(r"[YyNnQq]")
YES_PATTERN = re.compile(r"[Yy]")
NO_PATTERN = re.compile(r"[Nn]")
QUIT_PATTERN = re.compile(r"[Qq]")

QUERY_LIMIT = 10
STOPWORDS = get_stopwords()

try:
    nltk.data.find("corpora/wordnet.zip")
except LookupError:
    nltk.download("wordnet")


def display_results_and_ask_user_relevance(top10_results):
    """

    Args:
        top10_results:

    Returns:

    """
    print("TOP 10 RESULTS:")
    print("===")

    user_relevances = []

    for idx, result in enumerate(top10_results):
        print("Result #{}".format(idx + 1))
        print("---")
        print("Link: {}".format(result.get(ResultField.LINK, "")))
        print("Title: {}".format(result.get(ResultField.TITLE, "")))
        print("Snippet: {}".format(result.get(ResultField.SNIPPET, "")))
        print()
        relevance = None
        while not isinstance(relevance, str) or not OPTIONS_PATTERN.match(relevance):
            relevance = input("Is this Relevant? [Yy/Nn] ")

        if isinstance(relevance, str):
            if YES_PATTERN.match(relevance):
                user_relevances.append(1)
            elif NO_PATTERN.match(relevance):
                user_relevances.append(0)
        else:
            raise ValueError("Error: relevance must by [Yy/Nn]!")
    return user_relevances


class FetchQ(object):
    def __init__(self, api_key, search_id, query, precision, use_stopwords=True, scrape_results=True):
        """TODO: implements the whole pipeline, calls fetch10, ask user feedbacks, call methods for query expansion,
        etc. (keep asking user for user relevance feedbacks)

        Args:
            api_key:
            search_id:
            query:
            precision:
        """
        self.api_key = api_key
        self.search_id = search_id
        self.initial_query = query
        self.target_precision = precision
        self.use_stopwords = use_stopwords
        if use_stopwords:
            self.stopwords = set(STOPWORDS)
        else:
            self.stopwords = None
        self.scrape_results = scrape_results

    def run(self):
        print(INIT_MSG)

        query = self.initial_query
        # fetch first top 10 results for the initial query
        top10_results = self.fetch_top10(query)
        # ask for user relevance feedback
        user_relevances = display_results_and_ask_user_relevance(top10_results)
        # do we need to fetch more queries? (check if relevance is 0, 1.0, or less than target precision)
        fetch_more = self.is_fetch_more(query=self.initial_query, relevances=user_relevances)


        query_count = QUERY_LIMIT

        while fetch_more and query_count > 0:
            # expand the previous query terms
            expanded_query = self.expand_query(query=query, user_relevances=user_relevances, results=top10_results)
            # fetch first top 10 results for the new expanded query
            top10_results = self.fetch_top10(expanded_query)
            # ask for user relevance feedback
            user_relevances = display_results_and_ask_user_relevance(top10_results)
            fetch_more = self.is_fetch_more(query=expanded_query, relevances=user_relevances)

            # update old query to the new query
            query = expanded_query

            # reduce count query
            query_count -= 1

    def update_stopwords(self, query):
        if self.use_stopwords:
            # keep stopwords that are initially in query
            query_list = query.split()
            for term in query_list:
                if term in self.stopwords:
                    self.stopwords.remove(term)

    def is_fetch_more(self, query, relevances):
        """

        Args:
            query:
            relevances:

        Returns:

        """
        relevance = sum(relevances) / 10.0
        fetch_more = False
        print(SUMMARY_MSG.format(query=query, user_precision=relevance))
        if relevance == 0:
            print("Couldn't find any relevant document.")
            print("Exiting the program...")
        elif relevance >= self.target_precision:
            print("Target precision reached or exceeded, finished searching.")
            print("Exiting the program...")
        else:
            print("Still below the desired precision of {target_precision}".format(
                target_precision=self.target_precision))
            fetch_more = True
        return fetch_more

    def fetch_top10(self, query):
        print(SEARCH_MSG.format(api_key=self.api_key,
                                search_id=self.search_id,
                                query=query,
                                precision=self.target_precision))

        top10_results = get_top10(self.api_key, self.search_id, query)

        return top10_results

    def expand_query(self, query, user_relevances, results):
        """TODO: Implement relevant methods for performing query expansion

        Args:
            query:
            user_relevances:
            results:

        Returns:

        """
        # transform_results_to_vector_space_model(results, query)
        print("Expand Query")
        print("===")

        # comment first trying out rochio
        self.update_top10_results(results)
        print("Indexing results ....")
        
        # Data preprocessing:
        # 1) stop word handling (handle corner / edge cases with to be or not to be), etc.
        self.update_stopwords(query)

        # Converts document and query to vector space model
        vsm = transform_results_to_vector_space_model(results, query, TEXT_FIELDS, self.stopwords)

        # Implements Query Expansion Algorithm, Rocchio
        expanded_query = rocchio_model(alpha=ALPHA, beta=BETA, gamma=GAMMA,
                                       vsm=vsm, relevances=user_relevances, query=query)
        print("Augmenting previous search terms with {expanded_query}".format(expanded_query=expanded_query))

        return expanded_query

    def update_top10_results(self, results):
        """Crawl webpages (if necessary) and add more text data to the results.

        Arguments:
            results {[type]} -- [description]
        """
        if self.scrape_results:
            print("Scraping results...")
            return crawl_and_scrape_pages(results)
