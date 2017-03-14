# !/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf8 :

"""
Simple Web client API using URLLIB2, BS4 and a API from WeatherUnderground.

@author: Jaume Giralt Barbé
"""

import sys
import urllib2
from bs4 import BeautifulSoup

api_key = None

location = "Lleida"
data_format = ".xml"


class WeatherClient(object):
    """Documentation for WeatherClient."""

    url_base = "http://api.wunderground.com/api/"
    url_service = {
        "almanac": "/almanac/almanac/q/CA/",
        "hourly": "/hourly/q/CA/",
        "satellite": "/satellite/q/CA/",
        "astronomy": "/astronomy/q/Spain/"
        }

    def __init__(self, api_key):
        """Create the class."""
        super(WeatherClient, self).__init__()
        self.api_key = api_key

    def get_web_page(self, location):
        """Documentation."""
        data = []
        for x in self.url_service:
            url = self.url_base + self.api_key + self.url_service[x] +\
                location + data_format
            f = urllib2.urlopen(url)
            temporal = f.read()
            data.append([x, temporal])
            f.close()
        return data

    def parse_almanac_data(self, data):
        """Documentation."""
        soup = BeautifulSoup(data, 'lxml')

        result = {}
        result["maximes"] = {}
        result["minimes"] = {}

        maximes = soup.find("temp_high")
        result["maximes"]["normal"] = \
            str(maximes.find("normal").find("c").text).replace('\'u', '') + \
            " C degrees"
        result["maximes"]["record"] = \
            str(maximes.find("record").find("c").text).replace('\'u', '') + \
            " C degrees"
        minimes = soup.find("temp_low")
        result["minimes"]["normal"] = \
            str(minimes.find("normal").find("c").text).replace('\'u', '') + \
            " C degrees"
        result["minimes"]["record"] = \
            str(minimes.find("record").find("c").text).replace('\'u', '') + \
            " C degrees"

        return result

    def parse_hourly_data(self, data):
        """Documentation."""
        soup = BeautifulSoup(data, 'lxml')
        times = int(raw_input("How many hours do you want for the forecast ?"))
        result = {}
        if times > 36 or times < 1:
            times = 1
        results = soup.find_all("forecast")
        for x in results:
            result[str(x.find("pretty").text).replace('\'u', '')] = {}
            result[str(x.find("pretty").text).replace('\'u', '')]["temp"] = \
                str(x.find("temp").find("metric").text).replace('\'u', '') + \
                " C degrees"
            result[str(x.find("pretty").text).replace('\'u', '')]\
                ["condition"] = str(x.find("condition").text).\
                replace('\'u', '')
            result[str(x.find("pretty").text).replace('\'u', '')]\
                ["uvi"] = str(x.find("uvi").text).replace('\'u', '')
            result[str(x.find("pretty").text).replace('\'u', '')]\
                ["humidity"] = str(x.find("humidity").text).replace('\'u', '')\
                + "%"
            result[str(x.find("pretty").text).replace('\'u', '')]["feelslike"]\
                = str(x.find("feelslike").find("metric").text)\
                .replace('\'u', '') + " C degrees"
            result[str(x.find("pretty").text).replace('\'u', '')]["temp"] = \
                str(x.find("temp").find("metric").text).replace('\'u', '') + \
                " C degrees"
            times -= 1
            if times < 1:
                break
        return result

    def parse_satellite_data(self, data):
        """Documentation."""
        soup = BeautifulSoup(data, 'lxml').find("satellite")
        result = {}
        result["image_url"] = str(soup.find("image_url").text).\
            replace('\'u', '')
        result["image_url_ir4"] = str(soup.find("image_url_ir4").text).\
            replace('\'u', '')
        result["image_url_vis"] = str(soup.find("image_url_vis").text).\
            replace('\'u', '')
        return result

    def parse_astronomy_data(self, data):
        """Documentation."""
        soup = BeautifulSoup(data, 'lxml').find("moon_phase")
        result = {}
        result["percentilluminated"] = \
            str(soup.find("percentilluminated").text) + "%"
        result["ageofmoon"] = str(soup.find("ageofmoon").text) + " days" 
        result["sunset"] = str(soup.find("sunset").find("hour").text.\
            replace('\'u', '')) + ":" + str(soup.find("sunset").\
            find("minute").text.replace('\'u', '')) + " h"
        result["sunrise"] = str(soup.find("sunrise").find("hour").text.\
            replace('\'u', '')) + ":" + str(soup.find("sunrise").\
            find("minute").text.replace('\'u', '')) + " h"
        result["moonset"] = str(soup.find("moonset").find("hour").text.\
            replace('\'u', '')) + ":" + str(soup.find("moonset").\
            find("minute").text.replace('\'u', '')) + " h"
        result["moonrise"] = str(soup.find("moonrise").find("hour").text.\
            replace('\'u', '')) + ":" + str(soup.find("moonrise").\
            find("minute").text.replace('\'u', '')) + " h"
        return result

    def get_data(self, data):
        """Get the web-page, read and return the results."""
        almanac = self.parse_almanac_data(data[3][1])
        hourly = self.parse_hourly_data(data[0][1])
        satellite = self.parse_satellite_data(data[1][1])
        astronomy = self.parse_astronomy_data(data[2][1])
        return almanac, hourly, satellite, astronomy

    def get_information(self, location):
        """Documentation."""
        data = self.get_web_page(location)
        data = self.get_data(data)
        return data

    def print_results(self, data):
        """Documentation."""
        for x in data:
            print x
            for y in data[x]:
                print y, ':', data[x][y]


if __name__ == "__main__":
    if not api_key:
        try:
            api_key = sys.argv[1]
            wc = WeatherClient(api_key)
            almanac, hourly, satellite, astronomy = \
                wc.get_information(location)
            print "------------------"
            print "ALMANAC"
            print "------------------"
            wc.print_results(almanac)
            print "------------------"
            print "HOURLY"
            print "------------------"
            wc.print_results(hourly)
            print "------------------"
            print "SATELLITE"
            print "------------------"
            for x in satellite:
                print x, ":", satellite[x]
            print "------------------"
            print "ASTRONOMY"
            print "------------------"
            for x in astronomy:
                print x, ":", astronomy[x]
        except IndexError:
            print "Error, No API key"
