import math
import re
from collections import defaultdict

def build_tfidf(documents):
    def tok(text):
        return re.findall(r'\b[a-z][a-z0-9\-]{1,30}\b', text.lower())
    df        = defaultdict(int)
    tokenised = []
    for doc in documents:
        tokens = tok(doc)
        tokenised.append(tokens)
        for t in set(tokens):
            df[t] += 1
    n   = len(documents)
    idf = {t: math.log((n + 1) / (c + 1)) + 1.0 for t, c in df.items()}
    return idf, tokenised
 
 
def tfidf_vec(tokens, idf):
    tf = defaultdict(float)
    for t in tokens:
        tf[t] += 1.0
    n = len(tokens) or 1
    return {t: (c / n) * idf.get(t, 1.0) for t, c in tf.items()}
 
 
def cosine(va, vb):
    dot = sum(va.get(k, 0) * v for k, v in vb.items())
    na  = math.sqrt(sum(v * v for v in va.values()))
    nb  = math.sqrt(sum(v * v for v in vb.values()))
    return 0.0 if na == 0 or nb == 0 else dot / (na * nb)
