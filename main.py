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
import datetime

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images


administrator = users.User("wenwenzhang1001@gmail.com")
administrator_name = "wenwenzhang1001@gmail.com"

with open('accurate_loc_new.json') as data_file:
    building_to_loc = json.load(data_file)

default_rate = 3.5

class Event(ndb.Model):
    name = ndb.StringProperty(required= True)
    description = ndb.StringProperty()
    cover_url=ndb.StringProperty(default='http://www.finecooking.com/images/no_image_ld.jpg')

    author_name = ndb.StringProperty(default="administrator_name")

    loc = ndb.GeoPtProperty(required=True,default=ndb.GeoPt(30.283464, -97.737395))
    building = ndb.StringProperty(default="NIL")
    room = ndb.StringProperty(default="NA")

    dt_start = ndb.DateTimeProperty(required=True)
    dt_end = ndb.DateTimeProperty(required=True)
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
        # locations = []
        buildings = []
        dts_start = []
        names = []

        if self.request.get("email") == administrator_name:
            delete_item = self.request.get('delete_item')
            if delete_item:
                tmp = ndb.gql("SELECT * FROM Event WHERE name = :1",delete_item).get()
                tmp.key.delete();

        for event in events:
            if event.dt_start > datetime.datetime.now():
                buildings.append(event.building)
                dts_start.append(str(event.dt_start))
                names.append(event.name)
        dictPassed = {'dts_start':dts_start, 'names':names,'buildings':buildings}
        jsonObj = json.dumps(dictPassed, sort_keys=True,indent=4, separators=(',', ': '))
        self.response.write(jsonObj)



class ViewOneEvent(webapp2.RequestHandler):
    def get(self):
        event_name = self.request.get("event_name")
        the_event = ndb.gql("SELECT * FROM Event WHERE name = :1",event_name).get()
        print event_name
        author = ndb.gql("SELECT * FROM Crowdworker WHERE name = :1",the_event.author_name).get()
        if author.name != administrator_name:
            try:
                ratings = str(author.score/author.rated_times)
            except Exception, e:
                ratings = None
            author_name = author.name
            # print "ratings: "+ratings
        else:
            ratings = None
            author_name = None

        dictPassed = {'dt_start': str(the_event.dt_start),
                      'dt_end': str(the_event.dt_end),
                      # 'location':the_event.loc,
                      'building': the_event.building,
                      'room': the_event.room,
                      'description': the_event.description,
                      'coverUrl': the_event.cover_url,
                      'linkage': the_event.linkage,
                      'ratings': ratings,
                      'author_name': author_name
                      }
        jsonObj = json.dumps(dictPassed, sort_keys=True,indent=4, separators=(',', ': '))
        self.response.write(jsonObj)


class GiveFeedback(webapp2.RequestHandler):
    def get(self):
        feedback = self.request.get('feedback')
        event_name = self.request.get('event_name')
        author_name = ndb.gql("SELECT * FROM Event WHERE name = :1",event_name).get().author_name
        author_object = ndb.gql("SELECT * FROM Crowdworker WHERE name = :1",author_name).get()
        author_object.rated_times +=1
        if feedback == "Yes":
            author_object.score +=5

        author_object.put()

class ViewAllWorkers(webapp2.RequestHandler):
    def get(self):
        workers = Crowdworker.query().fetch()
        names = []
        ratings = []
        tmp_dic = {}
        for worker in workers:
            names.append(worker.name)
            try:
                rating = worker.score/worker.rated_times
            except Exception, e:
                rating = default_rate
            tmp_dic[worker.name] = rating;

        sort_key=sorted(tmp_dic,key=tmp_dic.__getitem__,reverse=True)
        for key in sort_key:
            ratings.append(str(tmp_dic[key]))
            #ratings.append(str(rating))


        dictPassed = {'names':sort_key, 'ratings':ratings}
        jsonObj = json.dumps(dictPassed, sort_keys=True,indent=4, separators=(',', ': '))
        self.response.write(jsonObj)

class ViewOneWorker(webapp2.RequestHandler):
    def get(self):
        # events_loc = []
        events_build = []
        events_dt_start = []
        events_name = []
        worker_name = self.request.get('worker_name')
        delete_item = self.request.get('delete_item')
        worker =  ndb.gql("SELECT * FROM Crowdworker WHERE name = :1",worker_name).get()


        if delete_item:
            tmp = ndb.gql("SELECT * FROM Event WHERE name = :1",delete_item).get()
            tmp.key.delete();
            #ndb.delete()

        events = ndb.gql("SELECT * FROM Event WHERE ANCESTOR IS :1", ndb.Key('author_name', worker_name))
        for event in events:
            # events_loc.append(event.loc)
            events_build.append(event.building)
            events_name.append(event.name)
            events_dt_start.append(str(event.dt_start))


        dictPassed = {'events_name':events_name, 'events_dt_start':events_dt_start,'events_build':events_build}
        jsonObj = json.dumps(dictPassed, sort_keys=True,indent=4, separators=(',', ': '))
        self.response.write(jsonObj)


class MapView(webapp2.RequestHandler):
    """docstring for Mapview"""
    def get(self):
        events = Event.query().fetch()
        locations = []
        buildings = []
        names = []
        date = self.request.get("date")
        date = datetime.datetime.strptime(date, '%Y %m %d')
        print date


        for event in events:
            if str(event.dt_start)[0:10] == str(date)[0:10]:
                locations.append(str(event.loc))
                buildings.append(event.building)
                names.append(event.name)

        dictPassed = {'display_building':buildings, 'names':names,'display_location':locations}
        jsonObj = json.dumps(dictPassed, sort_keys=True,indent=4, separators=(',', ': '))
        self.response.write(jsonObj)

class CalendarView(webapp2.RequestHandler):
    def get(self):
        events = Event.query().fetch()
        # locations = []
        buildings = []
        dts_start = []
        dts_end = []
        names = []

        for event in events:
            # locations.append(event.loc)
            buildings.append(event.building)
            dts_start.append(str(event.dt_start))
            dts_end.append(str(event.dt_end))
            names.append(event.name)

        dictPassed = {'display_date': dts_start, 'dts_end': dts_end, 'display_name': names, 'buildings': buildings}
        jsonObj = json.dumps(dictPassed, sort_keys=True,indent=4, separators=(',', ': '))
        self.response.write(jsonObj)

class AddEventWeb(blobstore_handlers.BlobstoreUploadHandler):
    def get(self):

        worker_name = self.request.get("worker_name")
        worker_flag = ndb.gql("SELECT * FROM Crowdworker WHERE name = :1",worker_name).get()
        if worker_flag == None:
            new_worker = Crowdworker(name = worker_name)
            new_worker.put()


        event_build = self.request.get("building")
        if event_build in building_to_loc:
            event_loc = ndb.GeoPt(building_to_loc[event_build][0], building_to_loc[event_build][1])
        else:
            event_build = 'NIL'
            event_loc = ndb.GeoPt(building_to_loc[event_build][0], building_to_loc[event_build][1])

        event_dt_start = self.request.get("date_time1")
        event_dt_start = datetime.datetime.strptime(event_dt_start, '%b %d %Y %I:%M%p')
        event_dt_end = self.request.get("date_time2")
        event_dt_end = datetime.datetime.strptime(event_dt_end, '%b %d %Y %I:%M%p')

        event_name = self.request.get("event_name")
        event_room = self.request.get("room")
        event_description = self.request.get("details")
        thiscover_url = self.request.get("cover_url")
        event_url = self.request.get("event_url")

        try:
            upload = self.get_uploads()[0]
            new_event = Event(parent=ndb.Key('author_name', worker_name), cover_url=str(upload.key()), name=event_name, loc=event_loc, building=event_build, author_name=worker_name, dt_start=event_dt_start, dt_end=event_dt_end, room=event_room, description=event_description)
        except Exception, e:
            new_event = Event(parent=ndb.Key('author_name', worker_name), cover_url=thiscover_url, linkage=event_url, name=event_name, building=event_build, loc=event_loc, author_name=worker_name, dt_start=event_dt_start, dt_end=event_dt_end, room=event_room, description=event_description)

        new_event.put()

# http://freelunch-test1.appspot.com/AddEventWeb?worker_name=kevin.utexas@gmail.com&date_time1=Jan%201%202016%20%201:33PM&date_time2=Jan%201%202016%20%202:33PM&building=PCL&event_name=ECE%20Seminar&details=Some%20detailed%20information...&room=2.500

class AddEvent(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):

        worker_name = self.request.get("worker_name")
        worker_flag = ndb.gql("SELECT * FROM Crowdworker WHERE name = :1",worker_name).get()
        if worker_flag == None:
            new_worker = Crowdworker(name = worker_name)
            new_worker.put()


        event_build = self.request.get("building")
        print event_build;
        print self.request.get("event_name");
        print self.request.get("date_time1");
        print self.request.get("date_time2");

        if event_build in building_to_loc:
            event_loc = ndb.GeoPt(building_to_loc[event_build][0], building_to_loc[event_build][1])
        else:
            event_build = 'NIL'
            event_loc = ndb.GeoPt(building_to_loc[event_build][0], building_to_loc[event_build][1])

        event_dt_start = self.request.get("date_time1")
        event_dt_start = datetime.datetime.strptime(event_dt_start, '%Y %m %d %H %M')
        event_dt_end = self.request.get("date_time2")
        event_dt_end = datetime.datetime.strptime(event_dt_end, '%Y %m %d %H %M')

        event_name = self.request.get("event_name")
        event_room = self.request.get("room")
        event_description = self.request.get("details")

        try:
            upload = self.get_uploads()[0]
            print str(upload.key());
            new_event = Event(parent=ndb.Key('author_name', worker_name), cover_url=str(images.get_serving_url(upload.key())+"=s500"), name=event_name, loc=event_loc, building=event_build, author_name=worker_name, dt_start=event_dt_start, dt_end=event_dt_end, room=event_room, description=event_description)
        except Exception, e:
            new_event = Event(parent=ndb.Key('author_name', worker_name), name=event_name, building=event_build, loc=event_loc, author_name=worker_name, dt_start=event_dt_start, dt_end=event_dt_end, room=event_room, description=event_description)

        new_event.put()
        print "put succeussful"


class GetUploadURL(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/Addevent')
        upload_url = str(upload_url)
        dictPassed = {'upload_url':upload_url}
        print(upload_url)
        jsonObj = json.dumps(dictPassed, sort_keys=True,indent=4, separators=(',', ': '))
        self.response.write(jsonObj)

class ViewOnedayEvents(webapp2.RequestHandler):
    """docstring for ViewOnedayEvents"""
    def get(self):
        events_name =[]
        events_dt_start = []
        events_build = []
        date = self.request.get("date")
        events = Event.query().fetch()
        for event in events:
            event_date = str(event.dt_start)[0:10]
            #print event_date
            if date == event_date:
                events_build.append(event.building)
                events_name.append(event.name)
                events_dt_start.append(str(event.dt_start))



        dictPassed = {'events_name':events_name, 'events_dt_start':events_dt_start,'events_build':events_build}
        jsonObj = json.dumps(dictPassed, sort_keys=True,indent=4, separators=(',', ': '))
        self.response.write(jsonObj)

class ViewOnebuildingEvents(webapp2.RequestHandler):
    """docstring for ViewOnebuildingEvents"""
    def get(self):
        events_name =[]
        events_dt_start = []
        events_build = []
        building = self.request.get('building')
        events = Event.query().fetch()
        for event in events:
            if event.building == building:
                events_build.append(event.building)
                events_name.append(event.name)
                events_dt_start.append(str(event.dt_start))

        dictPassed = {'events_name':events_name, 'events_dt_start':events_dt_start,'events_build':events_build}
        jsonObj = json.dumps(dictPassed, sort_keys=True,indent=4, separators=(',', ': '))
        self.response.write(jsonObj)







app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/MapView',MapView),
    ('/CalendarView',CalendarView),
    ('/Addevent',AddEvent),
    ('/AddEventWeb', AddEventWeb),
    ('/GetUploadURL', GetUploadURL),
    ('/ViewOneEvent',ViewOneEvent),
    ('/ViewAllEvents',ViewAllEvents),
    ('/ViewOneWorker',ViewOneWorker),
    ('/ViewAllWorkers',ViewAllWorkers),
    ('/GiveFeedback',GiveFeedback),
    ('/ViewOnedayEvents',ViewOnedayEvents),
      ('/ViewOnebuildingEvents',ViewOnebuildingEvents)
], debug=True)


