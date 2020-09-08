import json
import os

import nltk
import pytest

from config import PROJECT_DIR
from fetchq import FetchQ
from ir_utils import tf_idf_model, rocchio_model, get_stopwords
from search_utils import TEXT_FIELDS


@pytest.fixture
def data():
    with open("../data/top10_results.json", "r") as fp:
        return json.load(fp)


def test_tf_idf_model(data):
    vsm = tf_idf_model(data, "cars", TEXT_FIELDS)
    assert vsm is not None


@pytest.fixture
def vsm(data):
    return tf_idf_model(data, "cars", TEXT_FIELDS)


def test_rocchio(vsm, data):
    relevances = [0, 1, 0, 1, 0, 1, 0, 0, 1, 0]

    new_query = rocchio_model(vsm, relevances, "cars")
    print(new_query)


def test_get_stopwords():
    print(get_stopwords())


def test_lemmatize():
    from nltk.stem import WordNetLemmatizer

    try:
        nltk.data.find("corpora/wordnet.zip")
    except LookupError:
        nltk.download("wordnet")

    lemmatizer = WordNetLemmatizer()
    print(lemmatizer.lemmatize("jaguars"))
