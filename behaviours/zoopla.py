#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from decimal import Decimal
import re
import cgi
from behaviours.behaviour import Behaviour
import lib.dt

class Zoopla(Behaviour):

    routes = {
        '^(get )?new properties': 'get_properties',
        '^(get )?properties': 'get_all_properties'
    }

    endpoints = {
        'listings': 'http://api.zoopla.co.uk/api/v1/property_listings.js'
    }

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.collection = 'properties'
        self.define_idle(self.get_properties, 24, lib.dt.datetime_from_time(13, 0))

    def get_all_properties(self):
        return self.get_properties(False)

    def get_properties(self, only_new=True):
        api_key = self.config.get('ZooplaAPI')

        args = [
            'latitude=' + '55.051059',  # 55.351874
            'longitude=' + '-1.745536',  #-2.2579164
            'api_key=' + api_key,
            'minimum_beds=' + '2',
            'property_type=' + 'houses',
            'radius=' + '1',
            'maximum_price=' + '280000',
            'page_size=' + '100',
            'order_by=' + 'age',
            'ordering=' + 'ascending',
            'listing_status=' + 'sale',
            'keywords=' + 'garden'
        ]

        json_str = self.__request(args)
        # print json_str.status_code
        if json_str.status_code == 403:
            return 'Error: ' + json_str.headers['X-Error-Detail-Header']

        listings = json_str.json()['listing']
        # print json.dumps(listings, indent=4, sort_keys=True)

        excluded_keywords = [
            'pegswood',
            'tenanted',
            'leasehold',
            'kirkhill'
        ]

        response = []
        for listing in listings:
            if only_new and not self.__save_if_new(listing):
                continue

            if any(word in listing['description'].lower() for word in excluded_keywords) or any(
                            word in listing['displayable_address'].lower() for word in excluded_keywords):
                continue
            price = '{:10,.2f}'.format(Decimal(listing['price']))

            # Remove HTML from description and shorten to first sentence
            tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
            no_tags = tag_re.sub('', listing['short_description'].split('.')[0] + '.')
            description = cgi.escape(no_tags).strip()
            if description.startswith("Summary"):
                description = description[7:]

            r = [
                listing['displayable_address'],
                '\n£' + price,
                '\n' + description,
                '\n' + listing['details_url'].split('?')[0]
            ]
            response.append(' '.join(r))
        self.__remove_old(listings)
        if only_new:
            self.act.user = self.config.get('Users').split(',')
        return '\n\n'.join(response)

    def __save_if_new(self, listing):
        if self.db.find('properties', {'id': listing['listing_id']}).count() > 0:
            return False

        self.db.insert('properties', {'id': listing['listing_id']})
        return True

    def __remove_old(self, listings):
        for p in self.db.find('properties'):
            found = False
            for listing in listings:
                if listing['listing_id'] == p['id']:
                    found = True
            if not found:
                self.db.delete(p)

    def __request(self, args):
        param_string = '&'.join(args)
        r = requests.get(self.endpoints['listings'] + '?' + param_string, verify=False)
        return r
