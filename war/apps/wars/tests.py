from django.test import TestCase
from .models import HashTag, Tweet, Battle, HashTagForm
from django.contrib.auth.models import User
from datetime import timedelta, datetime
from django.utils import timezone
from collections import defaultdict
import enchant
import string
from django.core.exceptions import ValidationError
import pytz


class TestModels(TestCase):
    def setUp(self):
        self.now = timezone.now()
        self.later = self.now + timedelta(hours=1)
        self.user = User.objects.create(
            username='test user',
            email='testuser1@foo.com')
        self.user.save()
        self.hashtag = HashTag.objects.create(
            hashtag='#potus',
            user=self.user,
            start_time=self.now,
            end_time=self.later
        )
        self.hashtag.save()

        self.tweet = Tweet.objects.create(
            id=1001,
            content='Quick brown fox')
        self.tweet.save()
        self.tweet.hashtags = (self.hashtag, )
        self.tweet.save()

    def test_user(self):
        self.assertEqual(self.user.username, 'test user')
        self.assertEqual(self.user.email, 'testuser1@foo.com')

    def test_hashtag(self):
        self.assertEqual(self.hashtag.hashtag, "#potus")
        self.assertEqual(self.user, self.hashtag.user)
        self.assertIsNotNone(self.hashtag.created)

    def test_tweet(self):
        self.assertEqual(self.tweet.content, 'Quick brown fox')
        self.assertIn(self.hashtag, self.tweet.hashtags.all())

    def test_battle(self):
        user2 = User.objects.create(
            username='test user2',
            email='testuser2@foo.com')
        user2.save()
        b = Battle(user_red=self.user,
            user_blue=user2,
            hashtag=self.hashtag
        )
        b.save()
        self.assertEqual(b.user_red, self.user)
        self.assertEqual(b.user_blue, user2)
        self.assertEqual(b.hashtag, self.hashtag)

    def tearDown(self):
        self.hashtag.delete()
        self.tweet.delete()

    def test_start_time_valid(self):
        start_time = datetime(2010, 1, 1, 1, 1, 1, 1, pytz.UTC)
        hashtag = HashTag.objects.create(
            hashtag='#potus',
            user=self.user,
            start_time=start_time,
            end_time=self.later
        )
        with self.assertRaises(ValidationError):
            hashtag.full_clean()

    def test_hashtag_validation(self):
        later = timezone.now() + timedelta(days=1)
        earlier = timezone.now()
        hashtag_form = HashTagForm(
            {
                'hashtag': '#foobar',
                'user': self.user,
                'start_time': later,
                'end_time': earlier
            },
            instance=HashTag.objects.create(
                hashtag='#somename',
                user=self.user,
                start_time=later,
                end_time=earlier
            )
        )
        with self.assertRaises(ValidationError):
            hashtag_form.is_valid()


class TestTwitterAPI(TestCase):
    """
    This is NOT a unit test
    """
    def setUp(self):
        from .import twitter_settings
        import tweepy
        from tweepy.parsers import JSONParser
        self.d = enchant.Dict("en_US")

        consumer_key = getattr(twitter_settings, 'CONSUMER_KEY', None)
        consumer_secret = getattr(twitter_settings, 'CONSUMER_SECRET', None)
        access_token = getattr(twitter_settings, 'ACCESS_TOKEN', None)
        access_token_secret = getattr(twitter_settings, 'ACCESS_TOKEN_SECRET', None)

        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(self.auth, parser=JSONParser())

    def test_hashtag(self):
        errors = defaultdict(int)
        query = '#iggypop'
        result = self.api.search(query, count=20, lang='en')

        print(result.keys())
        for item in result.get('statuses'):
            print(item.get('id'))
            print(item.get('text'))
            # errors.append(self.chkr.set_text(item.get('text')))
            for w in item.get('text').split():
                w.strip(string.punctuation)
                if not self.d.check(w):
                    errors[w] += 1
                # err = self.d.check(item.get('text'))
                # errors.append(err)

        for word in errors.keys():
            if errors[word] > 1:
                print(word, errors[word])

        self.assertTrue(result is not None)
