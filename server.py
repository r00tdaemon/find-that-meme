import os

import motor.motor_tornado
import tornado.ioloop
import tornado.web
from textblob import TextBlob as tb

from build_index import cos_sim, tfidf


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", query="", memes=[])

    async def post(self):
        db = self.settings["db"]
        coll = db.scores
        q = self.get_argument("query").replace(",", " ").lower()
        q = tb(q)
        scores = {word: tfidf(word, q, [q]) for word in q.words}
        sims = []
        async for doc in coll.find():
            sims.append((doc["meme_id"], cos_sim(scores, doc["scores"])))

        sims = sorted(sims, key=lambda x: x[1], reverse=True)[:12]

        cursor = db.memes.find({"_id": {"$in": [x[0] for x in sims]}}, {"img": False})
        memes = await cursor.to_list(length=12)
        memes = sorted(memes, key=lambda x: [oid[0] for oid in sims].index(x["_id"]))

        self.render("index.html", query=str(q), memes=memes, similarity=sims)


def main():
    muser = os.environ.get("MONGOUSER")
    mpass = os.environ.get("MONGOPASS")
    client = motor.motor_tornado.MotorClient("mongodb://{}:{}@ds133856.mlab.com:33856/memes".format(muser, mpass))
    db = client["memes"]

    app = tornado.web.Application(
        [
            (r"/", MainHandler),
        ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True,
        db=db
    )
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
