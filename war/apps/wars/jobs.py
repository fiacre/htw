from rq import Queue
from redis import Redis
from rq.decorators import job
import time
from wars import SpellChecker


# @job()
# def count_spelling_errors():
#     sc = SpellChecker()
#     redis_conn = Redis()
#     q = Queue(connection=redis_conn)

#     job = q.enqueue(spelling_errors)    
#     print(job.result)

#     time.sleep(2)
#     print(job.result)
