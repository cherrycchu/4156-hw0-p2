"""
"""
import os

DEBUG = True
USE_STOPWORDS = True
SCRAPE_RESULTS = True
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Rocchio Parameters
ALPHA = 1.0
BETA = 0.75
GAMMA = 0.0

LOG_SCALE_IF_SCRAPE = True
ALWAYS_ADD_TWO_TERMS = True
