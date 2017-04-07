from rq import Queue
from redis import Redis
from rq.decorators import job
import time
from .spell_check import SpellChecker


@job
def get_tweets_since(tweet_id):
    pass


@job('default', timeout=3600)
def count_spelling_errors(dt):
    sc = SpellChecker()
    redis_conn = Redis()
    q = Queue(connection=redis_conn)

    from random import randint

    time.sleep(dt)
    return randint(5, 20)

    # job = q.enqueue(spelling_errors)    
    # print(job.result)

    # time.sleep(dt)
    # print(job.result)
