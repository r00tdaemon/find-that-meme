import math
from textblob import TextBlob as tb


def tf(word, blob):
    return blob.words.count(word) / len(blob.words)


def n_containing(word, bloblist):
    return sum(1 for blob in bloblist if word in blob.words)


def idf(word, bloblist):
    return math.log(1 + len(bloblist) / n_containing(word, bloblist), 2)


def tfidf(word, blob, bloblist):
    return tf(word, blob) * idf(word, bloblist)


def cos_sim(query, scores):
    similarity = 0
    for term in query.keys():
        similarity += query[term] * scores.get(term, 0)
    return similarity


if __name__ == '__main__':
    import os
    import pymongo

    muser = os.environ.get("MONGOUSER")
    mpass = os.environ.get("MONGOPASS")
    client = pymongo.MongoClient("mongodb://{}:{}@ds133856.mlab.com:33856/memes".format(muser, mpass))
    db = client["memes"]

    bloblist = []
    id_list = []
    for meme in db.memes.find(projection={"img": False, "meme_type": False}):
        id_list.append(meme["_id"])
        bloblist.append(tb(" ".join(meme["description"])))

    for i, blob in enumerate(bloblist):
        print("Document {}".format(i + 1))
        scores = {word.replace(".", " "): tfidf(word, blob, bloblist) for word in blob.words}
        doc = {
            "meme_id": id_list[i],
            "scores": scores
        }
        db.scores.insert(doc)
