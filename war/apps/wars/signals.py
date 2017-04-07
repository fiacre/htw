# signals.py
from .models import Battle
from django.db.models.signals import post_save
from django.dispatch import receiver
from .jobs import count_spelling_errors
# impor


@receiver(post_save, sender=Battle, dispatch_uid='battle_start')
def start_battle(sender, instance=None, created=False, **kwargs):
    dt = instance.hashtag.end_time - instance.hashtag.start_time
    for u in [sender.user_red, sender.user_blue]:
        u.spelling_errors = count_spelling_errors.delay(dt)


    