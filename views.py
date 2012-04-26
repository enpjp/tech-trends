#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import csv
import unicodedata

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.ext.webapp import template

# Force Django to reload its settings.
#from django.conf import settings
#import django.core.handlers.wsgi
#import django.core.signals
#import django.db
#import django.dispatch.dispatcher



from django.http import HttpResponse


from urlparse import urlparse
import hashlib
import re
import time
from types import *

from datetime import datetime
from datetime import date
from datetime import timedelta
import urllib
import cgi
import random
import StringIO

#from django.utils.httpwrappers import HttpResponse


class HomePage(webapp.RequestHandler):
    def get(self):

## User control -------------------------------------------------------
        user = users.get_current_user()
	login_url = "%s" % users.create_login_url(self.request.uri)
	logout_url = "%s" % users.create_logout_url(self.request.uri)
	#login_url.replace("/&/g","&amp;")
	#logout_url.replace("/&/g","fred")
        if user:
 	    #self.response.out.write(""" <div class="login"><!-- login text here here --> You are logged-in as: %s <a href="%s">Logout</a><br></div>  """ % (user.nickname(), logout_url) )
	    logon_message = "You are logged-in as:"
	    user_nickname_or_url = user.nickname()
	    #Need to add this for account control:
	    check_account(self)
        else:
	 # Un-comment  this line to prevent access to the page
         #   self.redirect(users.create_login_url(self.request.uri))
	 # use this line to allow none signed in access
	    logon_message = "You will need to sign in with a valid gmail account to use this software."
	    user_nickname_or_url = """<a class= "login" href="%s">Login or Register</a>""" % login_url

## end user control ---------------------------------------------------------------
	pageTitle= 'Tech-Trends Website Builder'

        template_values = {
	#	'my_qr_code': my_qr_code,

		'login_url' : login_url,
		'logout_url' : logout_url,
		'logon_message' : logon_message,
		'user_nickname_or_url' : user_nickname_or_url,


            	'pageTitle': pageTitle,          
        }
	path = os.path.join(os.path.dirname(__file__), 'html/index.html')
        self.response.out.write(template.render(path, template_values))


class InfoPage(webapp.RequestHandler):
    def get(self):

## User control -------------------------------------------------------
        user = users.get_current_user()
	login_url = "%s" % users.create_login_url(self.request.uri)
	logout_url = "%s" % users.create_logout_url(self.request.uri)
        if user:
 	    #self.response.out.write(""" <div class="login"><!-- login text here here --> You are logged-in as: %s <a href="%s">Logout</a><br></div>  """ % (user.nickname(), logout_url) )
	    logon_message = "You are logged-in as:"
	    user_nickname_or_url = user.nickname()
	    #Need to add this for account control:
	    account_info = check_account(self)
        else:
	 # Un-comment  this line to prevent access to the page
         #   self.redirect(users.create_login_url(self.request.uri))
	 # use this line to allow none signed in access
	    logon_message = "You will need to sign in with a valid gmail account to use this software."
	    user_nickname_or_url = """<a class= "login" href="%s">Login or Register</a>""" % login_url
## end user control ---------------------------------------------------------------
	my_url = self.request.url
	my_path = self.request.path
	# trim off the leading slash and info.
	my_clean_path = my_path[6:len(my_path)]	

	#Adding a back button query to info and help cards so a back button link can be offered
	my_query = self.request.query
	my_query_urlparse = cgi.parse_qs(my_query)

	if "back_button" in my_query_urlparse:
		back_button_value = my_query_urlparse["back_button"]
		back_button = back_button_value[0]

	else:
		back_button = ""
	# This is set up user scanning while elimiating self scans
	# Will be included on the card list page.

	pageTitle= my_clean_path[0:(len(my_clean_path))]
	#Set some values that are used in the subscription process
	#Some might be useful on other pages too.
	days_to_end_of_subscription = "0"


	#Is logged in?
	if user:
		
		# get the user id
		user_id = user.user_id()
		login_check = "True"
		#my_cards = place_address.get(db.Key.from_path('place_address',user_id))	
		#page_not_exist(self)
		#if not my_cards:
		#Can't buy anthing until you have created a page
		#	login_check = "False"
		Date_created = account_info['Date_created']
		days_to_end_of_subscription = account_info['days_to_end_of_subscription']
		Date_created_date_string = str(Date_created)
		check_key_free = hashlib.sha224('Free subscription %s %s' %(user_id, Date_created_date_string )).hexdigest()
		check_key_annual = hashlib.sha224('Annual subscription %s %s' %(user_id, Date_created_date_string )).hexdigest()
		check_key_basic_plus = hashlib.sha224('Basic Account Plus %s %s' %(user_id, Date_created_date_string )).hexdigest()
		check_key_premium = hashlib.sha224('Premium subscription %s %s' %(user_id, Date_created_date_string)).hexdigest()
	else:
		login_check = "False"
		user_id = False
		check_key_free = "None"
		check_key_annual = "None"
		check_key_premium = "None"
		check_key_basic_plus = "None"
	

        template_values = {
	#	'my_qr_code': my_qr_code,
		'login_check' : login_check,
		'days_to_end_of_subscription' : int(days_to_end_of_subscription),
		'check_key_free' : check_key_free,
		'check_key_annual' : check_key_annual,
		'check_key_basic_plus' : check_key_basic_plus,		
		'check_key_premium' : check_key_premium,
		'login_url' : login_url,
		'logout_url' : logout_url,
		'logon_message' : logon_message,
		'user_nickname_or_url' : user_nickname_or_url,
		'back_button' : back_button,
            	'pageTitle': pageTitle,          
        }


	# We need a white list to control the valid info pages
	valid_list = ["what_can_it_do.html",
	"faq.html",
	"instructions.html",
	"subscribe.html",
	"about.html",
	"account_not_enabled.html",
	"expert.html",
	"download_complete.html",
	"upload_complete.html",
	"expired.html",
	"helpfields.html",
	"not_in_use.html",
	"advert_mini_web.html",
	"advert_business_card.html",
	"advert_go_to.html",
	"advert_location.html",
	"advert_offer_general.html",
	"advert_offer_estate_agent.html",
	"advert_offer_travel_agent.html",
	"advert_membership.html",
	"advert_service.html",
	"advert_guided_tour.html",	
	"advert_stock.html",
	"advert_living_documents.html",
	"how_to.html"

	]
	white_list = set(valid_list)
	path = os.path.join(os.path.dirname(__file__), 'html/%s' % my_clean_path)
	if os.path.exists(path) and my_clean_path in white_list :

        	self.response.out.write(template.render(path, template_values))
	else:
		# go to page not found if code not in the database
		pageTitle= 'Page Not Found'
        	template_values = {
			'pageTitle': pageTitle, 
			'my_url' : my_url,
			'my_path' : my_path,
			'full_url' : 'fred',
			'test' : 'test'


        	}
		path = os.path.join(os.path.dirname(__file__), 'html/page_not_found.html')
        	self.response.out.write(template.render(path, template_values))

##################################################################
##Functions here
####################################################################

def logon_check(self):

## User control -------------------------------------------------------
        user = users.get_current_user()
	login_url = "%s" % users.create_login_url(self.request.uri)
	logout_url = "%s" % users.create_logout_url(self.request.uri)
        if user:
 	    #self.response.out.write(""" <div class="login"><!-- login text here here --> You are logged-in as: %s <a href="%s">Logout</a><br></div>  """ % (user.nickname(), logout_url) )
	    logon_message = "You are logged-in as:"
	    user_nickname_or_url = user.nickname()
	    #Need to add this for account control:
	    account_info = check_account(self)
        else:
	 # Un-comment  this line to prevent access to the page
         #   self.redirect(users.create_login_url(self.request.uri))
	 # use this line to allow none signed in access
	    logon_message = "You will need to sign in with a valid gmail account to use this software."
	    user_nickname_or_url = """<a class= "login" href="%s">Login or Register</a>""" % login_url
## end user control ---------------------------------------------------------------




