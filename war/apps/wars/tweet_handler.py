from .models import HashTag, Tweet
from war.settings import settings_twitter
import tweepy
from tweepy.parsers import JSONParser
from collections import defaultdict
import string
import enchant

# TODO move to env
consumer_key = getattr(settings_twitter, 'CONSUMER_KEY', None)
consumer_secret = getattr(settings_twitter, 'CONSUMER_SECRET', None)
access_token = getattr(settings_twitter, 'ACCESS_TOKEN', None)
access_token_secret = getattr(settings_twitter, 'ACCESS_TOKEN_SECRET', None)


class TweetHandler:
    '''
        @kwargs: {'hashtag' : HashTag object}
        takes a hashtag obj, connects to twitter
        checks if there are any tweets in the DB and gets the latest ID
        searches for tweets with ID greater than all previous tweets that have
            the given hashtag
        counts the spelling errors in those tweets
        writes the tweet content and num spelling errors to the DB
    '''
    def __init__(self, *args, **kwargs):
        self.hashtags = HashTag.objects.get(kwargs.get('hashtag'))
        self.dictionary = enchant.Dict("en_US")

    def _connect_to_twitter(self):
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(self.auth, parser=JSONParser())

    def tweets(self):
        '''
        get the last id and search with hashtag since last id
        save tweets
        '''
        last_id = 0
        last_tweet = Tweet.objects.last()
        if last_tweet:
            last_id = last_tweet.id

        result = self.api.search(self.hashtags.hashtag, lang='en', since_id=last_id)
        for item in result.get('statuses'):
            print("ID: ", item.get('id_str'))
            print("Text: ", item.get('text'))
            print([hashtag.get('text') for hashtag in item.get('entities').get('hashtags')])
            tweet, created = Tweet.objects.get_or_create(
                id=int(item.get('id_str'))
            )
            if created:
                tweet.hashtags = [x.hashtag for x in self.hashtags]
                tweet.hashtags += [hashtag.get('text') for hashtag in item.get('entities').get('hashtags')]
                tweet.content = item.get('text')
                tweet.save()

            errors = self.spelling_errors(tweet.content)
            tweet.num_errors = sum(errors.values())
            tweet.save()

    def spelling_errors(self, text):
        errors = defaultdict(int)
        for w in text.split():
            w.strip(string.punctuation)
            if not self.dictionary.check(w):
                errors[w] += 1
        return errors
