from .models import HashTag, Tweet
from .import twitter_settings
import tweepy
from tweepy.parsers import JSONParser
from collections import defaultdict
import string
import enchant

# TODO move to env
consumer_key = getattr(twitter_settings, 'CONSUMER_KEY', None)
consumer_secret = getattr(twitter_settings, 'CONSUMER_SECRET', None)
access_token = getattr(twitter_settings, 'ACCESS_TOKEN', None)
access_token_secret = getattr(twitter_settings, 'ACCESS_TOKEN_SECRET', None)


class SpellChecker:
    def __init__(self, *args, **kwargs):
        self.hashtags = HashTag.objects.get(kwargs.get('hashtag'))
        self.dictionary = enchant.Dict("en_US")

    def _connect_to_twitter(self):
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(self.auth, parser=JSONParser())

    def _tweets(self):
        last_id = 0
        last_tweet = Tweet.objects.last()
        if last_tweet:
            last_id = last_tweet.id

        result = self.api.search(self.hashtag, lang='en', since_id=last_id)
        for item in result.get('statuses'):
            tweet, created = Tweet.objects.get_or_create(
                id=item.get('id'),
                content=item.get('text')
            )
            if created:
                tweet.hashtags = tuple([x for x in self.hashtags])
                tweet.save()
            errors = self._spelling_errors(tweet.content)
            tweet.num_errors = sum(errors.values())
            tweet.save()

    def _spelling_errors(self, text):
        errors = defaultdict(int)
        for w in text.split():
            w.strip(string.punctuation)
            if not self.dictionary.check(w):
                errors[w] += 1
        return errors
