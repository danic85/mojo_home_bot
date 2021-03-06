#!/usr/bin/python
# -*- coding: latin-1 -*-
# Source: https://github.com/xDHILEx/Shower-Thoughts/blob/master/Reddit.py

from random import randint
from profanity import profanity
from behaviours.behaviour import Behaviour
from lib import feeds


class Reddit(Behaviour):

    routes = {
        'thought of the day': 'shower_thought',
        'did you know|teach me something': 'did_you_know',
        'funny image': 'funny_image'
    }

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.define_idle(self.did_you_know, randint(100, 200))
        self.define_idle(self.shower_thought, randint(50, 120))
        self.define_idle(self.funny_image, randint(24, 72))

    def shower_thought(self):
        """ returns a (one) random shower thought """
        url = "http://www.reddit.com/r/showerthoughts/hot/.json"
        return self.__get_random_title(url)

    def did_you_know(self):
        """ returns a (one) random did you know """
        url = "http://www.reddit.com/r/didyouknow/hot/.json"
        text = self.__get_random_title(url)
        text = text.replace('DYK', 'Did you know')
        text = text.replace('DKY', 'Did you know')
        if "Did you know" not in text:
            text = 'Did you know ' + self.__lower_first(text)
        return text

    def funny_image(self):
        """ returns a (one) random shower thought """
        url = "http://www.reddit.com/r/funny/hot/.json"
        response = self.__get_json(url)

        for i in response['data']['children']:
            if '.jpg' in i['data']['url']:
                self.act.respond_photo(i['data']['url'], i['data']['title'])
                return ''

        return ''

    def __get_random_title(self, url):
        """ Returns a (one) random post title """
        try:
            titles = self.__get_titles(self.__get_json(url))
            post = titles[self.__rand()]
            retries = 20
            custom_badwords = ['reddit', 'redditor']
            profanity.load_words(custom_badwords)
            while profanity.contains_profanity(post):
                post = titles[self.__rand()]
                retries -= 1
                if retries < 1:
                    break

            return post
        except Exception as ex:
            return 'There is a feed problem at the moment: ' + str(ex)

    @staticmethod
    def __get_json(url):
        return feeds.get_json(url, None, [('User-Agent', 'Mozilla/5.0')])

    @staticmethod
    def __get_titles(json_obj):
        """ Passing in the json_obj, append the title of each post to titles list, returns titles list. """
        titles = []
        for i in json_obj['data']['children']:
            titles.append("%s" % i['data']['title'])
        return titles

    @staticmethod
    def __rand():
        """ Returns a random integer between 0 and 24 (Posts #1 - #25 on Reddit) """
        return randint(0, 24)

    @staticmethod
    def __lower_first(s):
        """ Return string with lowercase first letter (for prefixing text to sentence) """
        return s[0].lower() + s[1:]
