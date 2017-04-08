from django.test import TestCase
from .models import HashTag, Battle, BattleForm, Tweet
from django.contrib.auth.models import User
from datetime import timedelta, datetime
from django.utils import timezone
from collections import defaultdict
import enchant
import string
from django.core.exceptions import ValidationError
import pytz
from unittest import mock
from django.db.models.signals import post_save


class TestModels(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='test user',
            email='testuser@foo.com'
        )
        self.user.save()
        self.now = timezone.now()
        self.later = self.now + timedelta(hours=1)
        self.hashtag = HashTag.objects.create(
            hashtag='#potus',
            # start_time=self.now,
            # end_time=self.later,
            user=self.user
        )
        self.hashtag.save()

    def test_hashtag(self):
        self.assertEqual(self.hashtag.hashtag, "#potus")
        self.assertEqual(self.hashtag.user, self.user)
        self.assertIsNotNone(self.hashtag.created)

    def test_hashtag_str(self):
        user = User.objects.create(
            username="foobar",
            email="abcdefg@foo.com"
        )
        user.save()
        hashtag = HashTag.objects.create(
            user=user,
            hashtag="#abcd"
        )
        hashtag.save()

        self.assertIsNotNone(str(hashtag))
        self.assertEqual(str(hashtag), "HashTag: #abcd, foobar")

    # def test_battle(self):
    #     user1 = User.objects.create(
    #         username='test user1',
    #         email='testuser1@foo.com'
    #     )
    #     user1.save()
    #     user2 = User.objects.create(
    #         username='test user2',
    #         email='testuser2@foo.com')
    #     user2.save()
    #     b = Battle(user_red=user1,
    #         user_blue=user2,
    #         hashtag=self.hashtag
    #     )
    #     b.save()
    #     self.assertEqual(b.user_red, user1)
    #     self.assertEqual(b.user_blue, user2)
    #     self.assertEqual(b.hashtag, self.hashtag)        

    @mock.patch('war.apps.wars.jobs.count_spelling_errors.delay')
    def test_battle_start_time_validate(self, cse):
        start_time = datetime(2010, 1, 1, 1, 1, 1, 1, pytz.UTC)
        user2 = User.objects.create(
            username='test_user2',
            email="test123@foo.com"
        )
        user2.save()
        hashtag2 = HashTag.objects.create(
            hashtag="#President",
            user=user2
        )
        battle = Battle.objects.create(
            hashtag_right=self.hashtag,
            hashtag_left=hashtag2,
            start_time=start_time,
            end_time=self.later
        )
        with self.assertRaises(ValidationError):
            battle.full_clean()

    @mock.patch('war.apps.wars.jobs.count_spelling_errors.delay')
    def test_battle_validation(self, cse):
        later = timezone.now() + timedelta(days=1)
        earlier = timezone.now()
        battle_form = BattleForm(
            {
                'hashtag_right': '#foobar',
                'hashtag_left': '#blah',
                'start_time': later,
                'end_time': earlier
            },
            instance=Battle.objects.create(
                hashtag_left=HashTag.objects.create(
                    hashtag='#somename',
                    user=User.objects.create(
                        username="erret",
                        email="ert@foo.com"
                    )
                ),
                hashtag_right=HashTag.objects.create(
                    hashtag='#someother',
                    user=User.objects.create(
                        username="foobar",
                        email="bar@foo.com"
                    )
                ),
                start_time=later,
                end_time=earlier
            )
        )
        with self.assertRaises(ValidationError):
            battle_form.is_valid()


class TestBattle(TestCase):
    def setUp(self):
        self.user_left = User.objects.create(
            username="testabc",
            email="tastabc@foo.com"
        )
        self.user_right = User.objects.create(
            username="test123",
            email='test123@foo.com'
        )
        self.user_right.save()
        self.user_left.save()
        self.hashtag_left = HashTag.objects.create(
            user=self.user_left,
            hashtag="#potus"
        )
        self.hashtag_right = HashTag.objects.create(
            hashtag='#slotus',
            user=self.user_right
        )
        self.hashtag_left.save()
        self.hashtag_right.save()
        self.battle = Battle.objects.create(
            hashtag_left=self.hashtag_left,
            hashtag_right=self.hashtag_right,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(seconds=30)
        )

    @mock.patch('war.apps.wars.jobs.count_spelling_errors.delay')
    def test_post_save_signal(self, cse):
        with mock.patch('war.apps.wars.signals.start_battle') as mock_signal:
            post_save.connect(mock_signal, sender=Battle, dispatch_uid="test_start_battle")
            self.battle.save()
            self.assertEquals(mock_signal.call_count, 1)
        self.assertTrue(cse.called)


class TestTweet(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            username="this is a user",
            email='my_email@domain.com'
        )
        self.user2 = User.objects.create(
            username='this is also a user',
            email='myptheremail@domain.com'
        )
        self.user2.save()
        self.user2.save()
        self.hashtag1 = HashTag.objects.create(
            user=self.user1,
            hashtag="#somehashtag"
        )
        self.hashtag2 = HashTag.objects.create(
            user=self.user2,
            hashtag="#anotherhashtag"
        )
        self.hashtag1.save()
        self.hashtag2.save()
        self.tweet = Tweet.objects.create(
            id=824794161878597633,
            content="some content"
        )
        self.tweet.save()

    def test_add_hashtags(self):
        self.tweet.hashtags = [self.hashtag1.hashtag, self.hashtag2.hashtag]
        self.tweet.save()
        self.assertEqual(self.tweet.hashtags, [self.hashtag1.hashtag, self.hashtag2.hashtag])
        self.assertEqual(self.tweet.num_errors, None)
        self.tweet.num_errors = 3
        self.tweet.save()
        self.assertEqual(self.tweet.num_errors, 3)


class TestTwitterAPI(TestCase):
    """
    This is NOT a unit test
    """
    def setUp(self):
        from war.settings import settings_twitter
        import tweepy
        from tweepy.parsers import JSONParser
        self.d = enchant.Dict("en_US")

        consumer_key = getattr(settings_twitter, 'CONSUMER_KEY', None)
        consumer_secret = getattr(settings_twitter, 'CONSUMER_SECRET', None)
        access_token = getattr(settings_twitter, 'ACCESS_TOKEN', None)
        access_token_secret = getattr(settings_twitter, 'ACCESS_TOKEN_SECRET', None)

        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(self.auth, parser=JSONParser())

    def test_hashtag(self):
        errors = defaultdict(int)
        query = '#iggypop'
        result = self.api.search(query, count=20, lang='en')

        # print(result.keys())
        for item in result.get('statuses'):
            # print(item.get('id'))
            # print(item.get('text'))
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
