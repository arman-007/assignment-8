import unittest
from scrapy.http import HtmlResponse
from scrapy_project.spiders.hotels_spider import HotelsSpider
import json

class TestHotelsSpider(unittest.TestCase):
    def setUp(self):
        self.spider = HotelsSpider()

    def test_parse(self):
        # Simulated response with mock data for locations
        body = '<script>window.IBU_HOTEL = {"initData": {"htlsData": {"inboundCities": [{"id": 1, "name": "Test City 1"}, {"id": 2, "name": "Test City 2"}], "outboundCities": [{"id": 3, "name": "Test City 3"}]}}}</script>'
        response = HtmlResponse(url="https://uk.trip.com/hotels/?locale=en-GB&curr=GBP", body=body, encoding='utf-8')

        results = list(self.spider.parse(response))
        self.assertEqual(len(results), 3)  # Ensure 3 requests are generated

    def test_parse_hotels(self):
        # Simulated response for hotel list
        body = '<script>window.IBU_HOTEL = {"initData": {"firstPageList": {"hotelList": [{"hotelBasicInfo": {"hotelName": "Hotel A", "price": 100}, "commentInfo": {"commentScore": 4.5}, "positionInfo": {"positionName": "Downtown", "coordinate": {"lat": 10.1, "lng": 20.2}}}]}}}</script>'
        response = HtmlResponse(url="https://uk.trip.com/hotels/list", body=body, encoding='utf-8')

        results = list(self.spider.parse_hotels(response))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["property_title"], "Hotel A")
        self.assertEqual(results[0]["price"], 100)
        self.assertEqual(results[0]["location"], "Downtown")
