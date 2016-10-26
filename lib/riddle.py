#!/usr/bin/env python
# -*- coding: utf-8 -*-

#riddle
from HTMLParser import HTMLParser
from random import randint

riddles = []
riddle = {}
riddleIndex = 0

# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        # print "Encountered a start tag:", tag
        self.currentTag = tag

    def handle_endtag(self, tag):
        # print "Encountered an end tag :", tag
        self.currentTag = ''

    def handle_data(self, data):
        # print "Encountered some data  :", data
        # print "currentTag: " + self.currentTag
        if (self.currentTag == 'em'):
            # print "setting answer"
            self.riddle['answer'] = data
            riddles.append(self.riddle)
        elif (self.currentTag == 'li'):
            # print "setting question"
            self.riddle = {'question': data, 'answer': ''}

def get_riddles(self):
    parser = MyHTMLParser()
    f = open(self.dir + '/' + self.config.get('Config','RiddleFile'), 'r')
    parser.feed(f.read())
    return riddles
    
# def get_question(self):
#     if (len(riddles) == 0):
#         riddleIndex = 0
#         parser = MyHTMLParser()
#         f = open(self.dir + '/' + self.config.get('Config','RiddleFile'), 'r')
#         parser.feed(f.read())
#         
#     if (riddleIndex >= len(riddles)):
#         riddleIndex = 0
#     riddle = riddles[riddleIndex]
#     print riddle
#     riddleIndex += 1
#     return riddle