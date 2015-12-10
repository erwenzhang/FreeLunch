import requests
import bs4
import re
import argparse
from multiprocessing import Pool

def monthToInt(month):
    return {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12
    }[month]

class UtEvents:
    keywords = ['free+food', 'pizza', 'drink', 'free']
    root_url = 'http://calendar.utexas.edu/search/events?search='
    events = []

    def get_event_page_urls(self, index_url):
        response = requests.get(index_url)
        soup = bs4.BeautifulSoup(response.text)
        all_urls = [a.attrs.get('href') for a in soup.select('div.item.event_item.vevent div.item_content_medium a[href^=http://calendar.utexas.edu/event]')]
        return all_urls[::2] # even index elements(staring from 0)
        # return soup.prettify()

    def get_event_data(self, event_page_url):
        event_data = {}
        response = requests.get(event_page_url)
        soup = bs4.BeautifulSoup(response.text)
        start = soup.select('div.box_header.vevent h2 abbr.dtstart')[0].get_text()
        event_data['start'] = re.sub('\\n {2,}', '', start)
        try:
            event_data['end'] = soup.select('div.box_header.vevent h2 abbr.dtend')[0].get_text()
        except Exception, e:
             event_data['end'] = 'None'

        title = soup.select('div.box_header.vevent h1.summary span')[0].get_text()
        event_data['title'] = re.sub('\\n {2,}', '', title)
        location = soup.select('div.box_header.vevent h3.location')[0].get_text()
        try:
            description = soup.select('div.box_header.vevent p.description')[0].get_text()
        except Exception, e:
            description = 'None'

        event_data['description'] = description#re.sub('\\n {2,}', '', description)
        event_data['location'] = re.sub('\\n {2,}', '', location)
        try:
            event_data['event_url'] = soup.select('div.extra_details dd.event-website a.url')[0].get_text()
        except Exception, e:
            event_data['event_url'] = 'None'

                # event_data['image_url'] = soup.select('div.box_image a[ref^=ibox]')[0].get_text()
                # event_data['youtube_url'] = soup.select('div#sidebar a[href^=http://www.youtube.com]')[0].get_text()
        return event_data

    def show_event_stats(self):
        for keyword in self.keywords:
            index_url = self.root_url + keyword
            event_page_urls = self.get_event_page_urls(index_url)
            for url in event_page_urls:
                # print(get_event_data(url))
                self.events.append(self.get_event_data(url))
        self.events = {v['title']:v for v in self.events}.values()

    # # for multiprocessing
    # def show_event_stats_using_multiprocessing(options):
    #     pool = Pool(options.workers)
    #     event_page_urls = get_event_page_urls()
    #     results = pool.map(get_event_data, event_page_urls)
    #     print(results)

    # def parse_args():
    #     parser = argparse.ArgumentParser(description = 'Show events data.')
    #     parser.add_argument('--workers', type = int, default = 8,
    #                         help = 'number of workers to use, 8 by default.')
    #     return parser.parse_args()
    # end of multiprocessing and parse_args

if __name__ == '__main__':
    freeEvents = UtEvents()
    freeEvents.show_event_stats()
    eventslist = freeEvents.events
    month = eventslist[0]['start'].split(', ')[1].split(' ')[0]
    day = int(eventslist[0]['start'].split(', ')[1].split(' ')[1])
    print monthToInt(month)
    print eventslist
    print 'Found ' + str(len(freeEvents.events)) + ' events.'
