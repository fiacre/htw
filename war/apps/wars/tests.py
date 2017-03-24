from django.test import TestCase
from .models import HashTag, Tweet, Battle, HashTagForm
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from collections import defaultdict
import enchant
import string
from django.core.exceptions import ValidationError


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
        # self.assertIsNotNone(self.tweet.uuid)
        # self.assertIsNotNone(self.tweet.created)

    def tearDown(self):
        self.hashtag.delete()
        self.tweet.delete()

    def test_hashtag_validation(self):
        with self.assertRaises(ValidationError):
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

            # hashtag = HashTag.objects.create(
            #     hashtag='#somename',
            #     user=self.user,
            #     start_time=later,
            #     end_time=earlier
            # )
            # hashtag.save()
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
