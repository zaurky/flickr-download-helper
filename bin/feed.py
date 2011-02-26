#!/usr/bin/python

import feedparser

rss="http://api.flickr.com/services/feeds/photos_friends.gne?user_id=53753127@N03&friends=0&display_all=1"

d = feedparser.parse(rss)
print d['feed']['title']
