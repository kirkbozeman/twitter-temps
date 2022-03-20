"""
One simple unittest on main function as an example.
This tests if the function errors if Twitter changes its API json output format.

Run from root of repo as: python -m test.unittests

"""

import unittest
import json

from app.core import get_place_and_temp_info, bbox_to_temp


class TestGoodBadTweets(unittest.TestCase):

    def test_tweet_bad_full_name(self):
        test_tweet_bad_full_name = b'{"data":{"geo":{"place_id":"4c6100a96901fb5e"},"id":"1505601775503659012","text":"@SuperCazarre CazarreSeum qu est ce que c bon"},"includes":{"places":[{"geo":{"type":"Feature","bbox":[5.2780296,43.1973118,5.5325183,43.3913065],"properties":{}},"id":"4c6100a96901fb5e"}]}}'
        includes = json.loads(test_tweet_bad_full_name).get('includes')
        with self.assertRaises(KeyError) as e:
            print(get_place_and_temp_info(includes))
        self.assertEqual(str(e.exception), "'full_name'")

    def test_tweet_bad_bbox(self):
        test_tweet_bad_bbox = b'{"data":{"geo":{"place_id":"4c6100a96901fb5e"},"id":"1505601775503659012","text":"@SuperCazarre CazarreSeum qu est ce que c bon"},"includes":{"places":[{"full_name":"Marseille, France","geo":{"type":"Feature","properties":{}},"id":"4c6100a96901fb5e"}]}}'
        includes = json.loads(test_tweet_bad_bbox).get('includes')
        with self.assertRaises(KeyError) as e:
            print(get_place_and_temp_info(includes))
        self.assertEqual(str(e.exception), "'bbox'")


if __name__ == '__main__':
    unittest.main()

