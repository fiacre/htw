# signals.py
from .models import Battle  # , Tweet
from django.db.models.signals import post_save
from django.dispatch import receiver
from .jobs import count_spelling_errors
# impor


@receiver(post_save, sender=Battle, dispatch_uid='battle_start')
def start_battle(sender, instance=None, created=False, **kwargs):
    dt = instance.end_time - instance.start_time
    num_errors = {}
    for h in [sender.hashtag_left, sender.hashtag_right]:

        # tweet = Tweet.objects.filter(hashtags__hashtag=h).last()
        # if tweet:
        num_errors[h] = count_spelling_errors.delay(dt)
        # else:
        #     print("Log an error e=here")


    