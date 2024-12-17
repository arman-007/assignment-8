import scrapy
import random
import json
import re
import os
from urllib.parse import urlparse

class HotelsSpider(scrapy.Spider):
    name = "hotels_combined"

    start_urls = [
        'https://uk.trip.com/hotels/?locale=en-GB&curr=GBP'
    ]

    def parse(self, response):
        """
        Step 1: Extract all locations and select 3 random ones.
        """
        self.logger.info("Fetching all locations...")

        # Extract the JavaScript variable using a regex
        script_data = re.search(r'window\.IBU_HOTEL\s*=\s*({.*?});', response.text)
        if script_data:
            data = json.loads(script_data.group(1))
            htls_data = data.get("initData", {}).get("htlsData", {})
            all_cities = htls_data.get("inboundCities", []) + htls_data.get("outboundCities", [])

            # Randomly select 3 cities
            selected_cities = random.sample(all_cities, 3)
            self.logger.info(f"Selected cities: {[city['name'] for city in selected_cities]}")

            for city in selected_cities:
                location_id = city.get("id")
                url = f"https://uk.trip.com/hotels/list?city={location_id}"
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_hotels,
                    meta={"city_name": city.get("name")}
                )
        else:
            self.logger.warning("Failed to extract location data.")

    def parse_hotels(self, response):
        """
        Step 2: Parse hotels for each location and yield data.
        """
        city_name = response.meta.get("city_name", "Unknown City")
        self.logger.info(f"Scraping hotels for location: {city_name}")

        # Extract JSON hotel data from page source
        script_data = re.search(r'window\.IBU_HOTEL\s*=\s*({.*?});', response.text)
        if script_data:
            data = json.loads(script_data.group(1))
            hotel_list = data.get("initData", {}).get("firstPageList", {}).get("hotelList", [])

            for hotel in hotel_list:
                # Extract hotel details
                hotel_data = {
                    "property_title": hotel.get("hotelBasicInfo", {}).get("hotelName", "N/A"),
                    "rating": hotel.get("commentInfo", {}).get("commentScore", "N/A"),
                    "location": hotel.get("positionInfo", {}).get("positionName", "N/A"),
                    "latitude": hotel.get("positionInfo", {}).get("coordinate", {}).get("lat", "N/A"),
                    "longitude": hotel.get("positionInfo", {}).get("coordinate", {}).get("lng", "N/A"),
                    "room_type": hotel.get("roomInfo", {}).get("physicalRoomName", "N/A"),
                    "price": hotel.get("hotelBasicInfo", {}).get("price", "N/A"),
                    "image_url": hotel.get("hotelBasicInfo", {}).get("hotelImg", None),
                    "city_name": city_name
                }

                # Skip if image is missing
                if not hotel_data["image_url"]:
                    self.logger.warning(f"Skipping hotel due to missing image: {hotel_data['property_title']}")
                    continue

                yield hotel_data
        else:
            self.logger.warning(f"No hotel data found for {city_name}")