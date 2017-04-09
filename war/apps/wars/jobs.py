from rq import Queue
from redis import Redis
from rq.decorators import job
import time
from .tweet_handler import TweetHandler


@job
def tweet_sentiment(tweet_id):
    pass


@job('default', timeout=3600)
def count_spelling_errors(dt, hashtag_obj):
    th = TweetHandler()
    redis_conn = Redis()
    q = Queue(connection=redis_conn)

    from random import randint

    time.sleep(dt)
    return randint(5, 20)

    # job = q.enqueue(spelling_errors)    
    # print(job.result)

    # time.sleep(dt)
    # print(job.result)
