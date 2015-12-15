import requests
import bs4
import re
import argparse
import json

class UtBuildings:
    root_url = 'https://www.utexas.edu/facilities/buildings'
    ut_url = 'https://www.utexas.edu'
    building_addresses = {}

    def get_building_page_urls(self, index_url):
        response = requests.get(index_url)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        all_urls = [(a.get_text(), a.attrs.get('href')) for a in soup.select('div.col-1-2 table.buildinglist a[href^=/facilities/buildings/UTM/]')]
        return all_urls

    def get_building_data(self, building_page_url):
        event_data = {}
        response = requests.get(self.ut_url + building_page_url)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        address = soup.select('h3')[0].get_text()
        return address

    def show_building_stats(self):
        building_page_urls = self.get_building_page_urls(self.root_url)
        for abbr, url in building_page_urls:
            self.building_addresses[abbr] = self.get_building_data(url)
            print abbr + ': ' + self.building_addresses[abbr]
        # self.building_addresses = {v['title']:v for v in self.building_addresses}.values()
        with open('building_addresses.json', 'w') as f:
            json.dump(self.building_addresses, f)

if __name__ == '__main__':
    build = UtBuildings()
    build.show_building_stats()
