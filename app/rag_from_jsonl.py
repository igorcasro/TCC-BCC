# Code created to convert the jsonl preprocessed data
# using RAG (Retrieval-Augmented Generation)

# First we thought about using word2vec but, after considerations, the BERT model
# probably will be better, considering the structure of the data we're dealing

import os
import glob
