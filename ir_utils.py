"""Utilities related to information retrieval methods for query expansion"""

import numpy as np
import pandas as pd

from collections import namedtuple
from sklearn.feature_extraction.text import TfidfVectorizer

from config import PROJECT_DIR, SCRAPE_RESULTS, LOG_SCALE_IF_SCRAPE, ALWAYS_ADD_TWO_TERMS

VectorSpaceModel = namedtuple("VectorSpaceModel", "doc_matrix, q_vector, terms")


class VSMType:
    TF_IDF = "TF_IDF"


def transform_results_to_vector_space_model(results, query, text_cols, stopwords=None, option=VSMType.TF_IDF):
    """

    Args:
        results:
        query:
        text_cols:
        stopwords:
        option:

    Returns:

    """
    if option == VSMType.TF_IDF:
        return tf_idf_model(results, query, text_columns=text_cols, stopwords=stopwords)


def tf_idf_model(results, query, text_columns, stopwords=None):
    """

    Args:
        results:
        query:
        text_columns:

    Returns:

    """
    df_text = pd.DataFrame(results)
    text_columns = list(set(df_text.columns).intersection(text_columns))
    df_text[text_columns] = df_text[text_columns].fillna("")

    # combine all text
    df_text['fulltext'] = ""
    for col in text_columns:
        df_text["fulltext"] += df_text[col] + " "

    text = df_text['fulltext'].tolist()

    if SCRAPE_RESULTS and LOG_SCALE_IF_SCRAPE:
        t_vectorizer = TfidfVectorizer(stop_words=stopwords, sublinear_tf=True)
    else:
        t_vectorizer = TfidfVectorizer(stop_words=stopwords)

    doc_matrix = t_vectorizer.fit_transform(text).toarray()
    q_vector = t_vectorizer.transform([query]).toarray()

    return VectorSpaceModel(doc_matrix=doc_matrix, q_vector=q_vector, terms=t_vectorizer.get_feature_names())


def rocchio_model(vsm, relevances, query, alpha=1.0, beta=0.75, gamma=0.0):
    """

    Args:
        vsm:
        relevances:
        alpha:
        beta:
        gamma:

    Returns:

    """
    rel_ids = [i for i in range(len(relevances)) if relevances[i] == 1]
    nrel_ids = [i for i in range(len(relevances)) if relevances[i] == 0]

    rel_mat = vsm.doc_matrix[rel_ids]
    nrel_mat = vsm.doc_matrix[nrel_ids]

    q_new = alpha * vsm.q_vector + \
            beta * 1 / len(rel_ids) * np.sum(rel_mat, axis=0) - \
            gamma * 1 / len(nrel_ids) * np.sum(nrel_mat, axis=0)

    q_new = q_new.clip(min=0)
    q_new = q_new.ravel()

    # order the terms in descending order of weights
    sorted_idx = np.argsort(q_new)[::-1]

    sorted_score = q_new[sorted_idx]
    sorted_terms = np.array(vsm.terms)[sorted_idx]

    # build new query based on rocchio weights
    new_query = []
    old_query_terms = query.split()

    old_norm_query = {term.lower():term for term in old_query_terms}
    old_query_idx = {term:i for i, term in enumerate(old_query_terms)}

    new_term_count = 0
    old_term_count = len(set(old_query_terms))

    diff_order = False

    for term in sorted_terms:
        if term in old_norm_query:
            old_term = old_norm_query[term]
            new_query.append(old_term)
            old_term_count -= 1

            if len(new_query) - 1 != old_query_idx[old_term]:
                diff_order = True
        elif new_term_count < 2:
            new_query.append(term)
            new_term_count += 1

        if ALWAYS_ADD_TWO_TERMS:
            if old_term_count == 0 and new_term_count == 2:
                break
        else:
            # new terms are 2 and exhausted all the old terms but the order is different
            if new_term_count == 2 or (old_term_count == 0 and diff_order):
                break
            else:
                # old term count is 0 but order is the same, but we have a new term
                if old_term_count == 0 and new_term_count > 0:
                    break

    # add old terms if it isn't in the new query
    for term in old_query_terms:
        if term not in new_query:
            new_query.append(term)

    return " ".join(new_query)


def get_stopwords():
    stopwords = set()

    try:
        with open(PROJECT_DIR + "/proj1-stop.txt", "r") as fp:
            stopwords = set(fp.read().split('\n'))
    except:
        pass

    return stopwords
