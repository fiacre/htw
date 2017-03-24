from django.db import models
from django.contrib.auth.models import User
from war.utils.base_model import TrackingModel
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from datetime import timedelta
from django.forms import ModelForm
from django.utils import timezone


def validate_is_later(start_time, end_time):
    if start_time > end_time:
        raise ValidationError(
            _('%(end) must be later than %(start'),
            params={'start': start_time, 'end': end_time},
        )


class HashTag(TrackingModel):
    ''' class for tracking hashtags
    '''
    # Todo Validate hashtag is a hashtag in the twitter sense
    hashtag = models.CharField(max_length=32, null=False)
    user = models.ForeignKey(User, default=1)
    start_time = models.DateTimeField(null=False, blank=True, default=timezone.now())
    # TODO : add validation that start_time > end_time
    end_time = models.DateTimeField(
        null=False,
        blank=True,
        default=timezone.now() + timedelta(seconds=60)
    )

    def __str__(self):
        return "HashTag: {}, {}, {}".format(self.hashtag, str(self.start_time), str(self.end_time))


class HashTagForm(ModelForm):
    def is_valid(self, *args, **kwargs):
        start_time = self['start_time'].value()
        end_time = self['end_time'].value()
        if start_time > end_time:
            raise ValidationError("Start_time must be earlier than end_time")
        super().is_valid(*args, **kwargs)

    class Meta:
        model = HashTag
        fields = ['hashtag', 'user', 'start_time', 'end_time']


class Tweet(TrackingModel):
    ''' class to track tweets
        has many hashtags
    '''
    id = models.IntegerField(primary_key=True)
    content = models.CharField(max_length=128)
    hashtags = models.ManyToManyField(HashTag)
    num_errors = models.IntegerField(null=True)

    def __str__(self):
        return self.content


class Battle(TrackingModel):
    user_red = models.ForeignKey(User, related_name='%(class)s_red')
    user_blue = models.ForeignKey(User, related_name='%(class)s_blue')
    hashtag = models.ForeignKey(HashTag)

    def __str__(self):
        return "Battle: {}, {}, {}".format(self.user_red, self.user_blue, self.hashtag)
