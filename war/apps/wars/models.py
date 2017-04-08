from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
from war.utils.base_model import TrackingModel
from django.core.exceptions import ValidationError
# from django.utils.translation import ugettext_lazy as _
from datetime import timedelta
from django.forms import ModelForm
from django.utils import timezone


def validate_future(dt):
    if dt < timezone.now():
        raise ValidationError(
            '{} is an invalid start time!'.format(dt)
        )


class HashTag(TrackingModel):
    ''' class for tracking hashtags
    '''
    # Todo Validate hashtag is a hashtag in the twitter sense
    hashtag = models.CharField(max_length=32, null=False)
    user = models.ForeignKey(User, null=False, blank=True)

    def __str__(self):
        return "HashTag: {}, {}".format(self.hashtag, self.user)


class Tweet(TrackingModel):
    ''' class to track tweets
        has many hashtags
    '''
    id = models.BigIntegerField(primary_key=True)
    content = models.CharField(max_length=128)
    hashtags = ArrayField(models.CharField(max_length=128, null=True), null=True)
    num_errors = models.IntegerField(null=True)

    def __str__(self):
        return self.content


class Battle(TrackingModel):
    hashtag_right = models.OneToOneField(HashTag, related_name='hashtag_right')
    hashtag_left = models.OneToOneField(HashTag, related_name='hashtag_left')
    start_time = models.DateTimeField(
        null=False, 
        blank=True, 
        default=timezone.now(), 
        validators=[validate_future]
    )
    end_time = models.DateTimeField(
        null=False,
        blank=True,
        default=timezone.now() + timedelta(seconds=60)
    )

    def __str__(self):
        return "{}, {}, {}, {}".format(
            self.hashtag_left, self.hashtag_right, self.start_time, self.end_time)


class BattleForm(ModelForm):
    def is_valid(self, *args, **kwargs):
        start_time = self['start_time'].value()
        end_time = self['end_time'].value()
        if start_time > end_time:
            raise ValidationError("Start_time must be earlier than end_time")
        super().is_valid(*args, **kwargs)

    class Meta:
        model = Battle
        fields = ['hashtag_right', 'hashtag_left', 'start_time', 'end_time']
