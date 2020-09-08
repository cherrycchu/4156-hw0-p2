#!/usr/bin/env python3

"""The command line interface for FetchQ, a query expansion tool for disambiguating queries."""

import sys

from googleapiclient.errors import HttpError

from config import USE_STOPWORDS, SCRAPE_RESULTS
from fetchq import FetchQ


cli_guide = '''Usage: {} [API_KEY] [SEARCH_ID] [TARGET_PRECISION] "[QUERY]"

Arguments:
- TARGET_PRECISION: a float between 0 to 1
- QUERY: word or sequence of words'''


def parse_cli_args():
    helper_msg = cli_guide.format(sys.argv[0])

    # check validity of input arguments
    if len(sys.argv) != 5:
        print(helper_msg)
    else:
        try:
            api_key, search_id, target_precision, query = sys.argv[1:]
            target_precision = float(target_precision)
            if not 0.0 <= target_precision <= 1.0:
                raise ValueError()
            return api_key, search_id, target_precision, query
        except ValueError:
            print("Error: Target precision value must be float between 0 or 1")


if __name__ == "__main__":
    fetch_q = None

    # Example command:
    # ./cli.py [SEARCH_API_KEY] [SEARCH_ID] 0.9 cars

    result = parse_cli_args()

    # check validity of return value of fetch query
    if result:
        api_key, search_id, target_precision, query = result
        fetch_q = FetchQ(api_key=api_key, search_id=search_id,
                         query=query, precision=target_precision,
                         use_stopwords=USE_STOPWORDS, scrape_results=SCRAPE_RESULTS)

        try:
            if fetch_q:
                fetch_q.run()
        except HttpError:
            raise ValueError("Wrong API Key or Search ID!")
