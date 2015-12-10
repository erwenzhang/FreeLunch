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
# limitations under the License
from __future__ import division
import webapp2
import cgi
import urllib
import json

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images


administrator1 = users.User("wenwenzhang1001@gmail.com")
administrator2 = users.User("kevin@utexas.edu.com")
administrator1_name = "wenwenzhang1001@gmail.com"
administrator2_name = "kevin@utexas.edu.com"

class Event(ndb.Model):
    name = ndb.StringProperty(required= True)
    description = ndb.StringProperty()
    coverurl=ndb.StringProperty(default=None)

    
    author_name = ndb.StringProperty(default="administrator")

    loc = ndb.GeoPtProperty(required=True,default=ndb.GeoPt(0,0))
    date = ndb.DateTimeProperty(required=True)

    linkage = ndb.StringProperty(default=None)


class Crowdworker(ndb.Model):
    name = ndb.StringProperty()
    rated_times = ndb.IntegerProperty(default=0)
    score = ndb.IntegerProperty(default=0)




class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')


class ViewAllEvents(webapp2.RequestHandler):
    def get(self):
        events = Event.query().fetch()
        locations = []
        dates = []
        names = []

        for event in events:
            if event.date > datetime.datetime.now()
                locations.append(event.loc))
                dates.append(event.date)
                names.append(event.name)
        dictPassed = {'dates':dates, 'names':names,'locations':locations}
        jsonObj = json.dumps(dictPassed, sort_keys=True,indent=4, separators=(',', ': '))
        self.response.write(jsonObj)



class ViewOneEvent(webapp2.RequestHandler):
    def get(self):
        event_name = self.request.get("event_name")
        the_event = ndb.gql("SELECT * FROM Event WHERE name = :1",event_name).get()
        print event_name
        author = ndb.gql("SELECT * FROM Crowdworker WHERE name = :1",the_event.author_name).get()
        if author.name != administrator1_name and author.name!= administrator2_name:
            ratings = str(author.score/author.rated_times)
            author_name = author.name
            print "ratings: "+ratings
        else:
            ratings = None
            author_name = None

        dictPassed = {'date':the_event.date,
                      'location':the_event.loc,
                      'description':the_event.description,
                      'coverUrl':the_event.coverUrl,
                      'linkage':the_event.linkage,
                      'ratings':ratings,
                      'author_name':author_name
                      }
        jsonObj = json.dumps(dictPassed, sort_keys=True,indent=4, separators=(',', ': '))
        self.response.write(jsonObj)


class GiveFeedback(webapp2.RequestHandler):
    def get(self):
        feedback = self.request.get('feedback')
        author_name = self.request.get('author_name')
        author = ndb.gql("SELECT * FROM Crowdworker WHERE name = :1",author_name).get()
        author.rated_times +=1
        if feedback == "Yes":
            author.score +=5

        author.put()

class ViewAllWorkers(webapp2.RequestHandler):
    def get(self):
        workers = Crowdworker.query().fetch()
        names = []
        ratings = []

        for worker in workers:
            names.append(worker.name)
            rating = worker.score/worker.rated_times
            ratings.append(str(rating))


        dictPassed = {'names':names, 'ratings':ratings}
        jsonObj = json.dumps(dictPassed, sort_keys=True,indent=4, separators=(',', ': '))
        self.response.write(jsonObj)

class ViewOneWorker(webapp2.RequestHandler):
    def get(self):
        events_loc = []
        events_date = []
        events_name = []
        worker_name = self.request.get('worker_name')
        delete_list = self.request.get('delete_list')
        worker =  ndb.gql("SELECT * FROM Crowdworker WHERE name = :1",worker_name).get())
        
        
        if delete_list:
            for delete_item in delete_list:
                ndb.delete(ndb.gql("SELECT * FROM Event WHERE name = :1",delete_item))

        events = ndb.gql("SELECT * FROM Event WHERE ANCESTOR IS :1",worker.ID).get())
        for event in events:
            events_loc.append(event.loc)
            events_name.append(event.name)
            events_date.append(event.date)


        dictPassed = {'events_name':events_name, 'events_date':events_date,'events_loc':events_loc}
        jsonObj = json.dumps(dictPassed, sort_keys=True,indent=4, separators=(',', ': '))
        self.response.write(jsonObj)


class MapView(webapp2.RequestHandler):
    """docstring for Mapview"""
    def get(self):
        events = Event.query().fetch()
        locations = []
        dates = []
        names = []

        for event in events:
            if event.date > datetime.datetime.now()
                locations.append(event.loc)
                dates.append(event.date)
                names.append(event.name)

        dictPassed = {'dates':dates, 'names':names,'locations':locations}
        jsonObj = json.dumps(dictPassed, sort_keys=True,indent=4, separators=(',', ': '))
        self.response.write(jsonObj)

class CalendarView(webapp2.RequestHandler):
    def get(self):
        events = Event.query().fetch()
        locations = []
        dates = []
        names = []

        for event in events:
            locations.append(event.loc)
            dates.append(event.date)
            names.append(event.name)

        dictPassed = {'dates':dates, 'names':names,'locations':locations}
        jsonObj = json.dumps(dictPassed, sort_keys=True,indent=4, separators=(',', ': '))
        self.response.write(jsonObj)

class AddEvent(blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        
        worker_name = self.request.get("worker_name")
        worker_flag = ndb.gql("SELECT * FROM Crowdworker WHERE worker_name = :1",worker_name).get()
        if worker_flag == None:
            new_worker = Crowdworker(ID = workerID,name = worker_name)
            new_worker.put()


        event_loc = self.request.get("loc")
        event_date = self.request.get("date")
        event_name = self.request.get("name")
        upload = self.get_uploads()[0]
        if upload:
            new_event = Event(parent=ndb.Key.from_path('author_name'),worker_name),coverurl=str(upload.key()),name = event_name,loc=event_loc,date=event_date,author_name=worker_name)
        else:
            new_event = Event(parent=ndb.Key.from_path('author_name'),worke_name),name = event_name,loc=event_loc,date=event_date,author_name=worker_name)
        new_event.put()
   



 

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/MapView',MapView),
    ('/CalendarView',CalendarView),
    ('/Addevent',AddEvent),
    ('/ViewOneEvent',ViewOneEvent),
    ('/ViewAllEvents',ViewAllEvents),
    ('/ViewOneWorker',ViewOneWorker),
    ('/ViewAllWorkers',ViewAllWorkers),
    ('/GiveFeedback',GiveFeedback)],
    debug = True)


