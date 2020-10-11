import random
import hashlib


def get_score(store, phone, email, birthday=None, gender=None, first_name=None, last_name=None):
    key = 'p#%se#%sb#%sg#%sfn#%sln#%s' % (phone, email, birthday, gender, first_name, last_name)
    key = hashlib.sha512(key.encode('utf-8')).hexdigest()

    score = store.cache_get(key) or 0
    if score:
        return float(score)
    else:
        score = 0
        if phone:
            score += 1.5
        if email:
            score += 1.5
        if birthday and gender:
            score += 1.5
        if first_name and last_name:
            score += 0.5
        store.cache_set(key, score, 60)
    return score


def get_interests(store, cid):
    key = 'i#%s' % cid
    result = store.get(key) or []
    result = [v.decode('utf-8') for v in result]
    return result
