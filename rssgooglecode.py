from google.appengine.api import urlfetch
import re

urlStr = 'http://code.google.com/p/tdrop/downloads/list'
reGoogleCode = 'vt id col_0">[^<]*<a href="([^"]*)[^>]*>([^<]*)</a>[^<]*</td>[^<]*<td[^<]*<[^>]*>([^<]*)<'

result = urlfetch.fetch(urlStr)
if result.status_code == 200:

	print 'Content-Type: application/rss+xml'
	print ''

	print """<?xml version="1.0"?>
	<rss version="2.0">
	  <channel>
	    <title>Teardrop downloads feed</title>
	    <link>http://www.teardrop.fr/download/</link>
	    <description>RSS 2.0 feed containing the latest Teardrop downloads</description>
	    <language>en-us</language>
	    <generator>rssGoogleCode, crafted by Olivier Coupelon</generator>
	    <webMaster>olivier.coupelon@teardrop.fr</webMaster>"""

	for m in re.finditer(reGoogleCode, result.content):
		print '    <item>'
		print '      <title>%s</title>' % m.group(3)
		print '      <link>%s</link>' % m.group(1)
		print '      <description>%s</description>' % m.group(2)
		print '    </item>'

	print """  </channel>
	</rss>"""
