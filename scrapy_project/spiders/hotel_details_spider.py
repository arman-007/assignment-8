# import scrapy
# import json
# import re


# class HotelDetailsSpider(scrapy.Spider):
#     name = "hotel_details"

#     def start_requests(self):
#         # Load the selected cities from the first spider's output
#         with open("random_3_hotels.json", "r") as f:
#             data = json.load(f)



#         # Access the first element of the list and get "selectedCities"
#         if isinstance(data, list) and len(data) > 0:
#             selected_cities = data[0].get("selectedCities", [])
#         else:
#             self.logger.error("Invalid JSON structure in random_3_hotels.json")
#             return
#         # print(selected_cities)
#         self.logger.info(f"Selected cities: {selected_cities}")

#         for city in selected_cities:
#             location_id = city["id"]
#             url = f"https://uk.trip.com/hotels/list?city={location_id}"
#             yield scrapy.Request(
#                 url=url,
#                 callback=self.parse_hotels,
#                 # meta={"city_name": city["name"]}
#             )
#             # print(response)

#     def parse_hotels(self, response):
#         # Extract the JavaScript variable using a regular expression
#         script_data = re.search(r'window\.IBU_HOTEL\s*=\s*({.*?});', response.text)
#         # print(response.text)

#         if script_data:
#             # Parse the JSON data
#             json_data_str = script_data.group(1)
#             self.logger.info("Successfully extracted JSON data from window.IBU_HOTEL.")
#             data = json.loads(json_data_str)

#         hotelList = data.get("initData", {}).get("firstPageList", {}).get("hotelList", {})
#         # print(len(hotelList))
#         for hotel in hotelList:
#             # different sections of each hotels
#             hotelBasicInfo = hotel.get("hotelBasicInfo", {})
#             commentInfo = hotel.get("commentInfo", {})
#             positionInfo = hotel.get("positionInfo", {})
#             roomInfo = hotel.get("roomInfo", {})
#             # print(hotel)

#             hotel_data = {
#                 "property_title" : hotelBasicInfo.get("hotelName", "N/A"),
#                 "rating" : commentInfo.get("commentScore", "N/A"),
#                 "location" : positionInfo.get("positionName", "N/A"),
#                 "latitude" : positionInfo.get("coordinate", {}).get("lat", "N/A"),
#                 "longitude" : positionInfo.get("coordinate", {}).get("lng", "N/A"),
#                 "room_type" : roomInfo.get("physicalRoomName", "N/A"),
#                 "price" : hotelBasicInfo.get("price", "N/A"),
#                 "image_url" : hotelBasicInfo.get("hotelImg", None)
#             }
#             if hotel_data.get("image_url") is None:
#                 self.logger.warning(f"Missing image for hotel: {hotel_data['property_title']}")
#                 continue  # Skip this hotel if no image is available

#             # Only yield item if data is valid
#             if hotel_data["property_title"] != "N/A":
#                 yield hotel_data
#             else:
#                 self.logger.warning(f"Skipping hotel due to missing data: {hotel_data['property_title']}")

import scrapy
import json
import re
import os
import psycopg2
from urllib.parse import urlparse


class HotelDetailsSpider(scrapy.Spider):
    name = "hotel_details"

    def start_requests(self):
        """
        Connect to the database and fetch location IDs to start requests.
        """
        db_url = os.getenv("DATABASE_URL")  # Read database URL from environment
        if not db_url:
            self.logger.error("DATABASE_URL is not set in environment variables.")
            return

        # Parse the database URL for psycopg2
        result = urlparse(db_url)
        db_params = {
            "dbname": result.path.lstrip('/'),
            "user": result.username,
            "password": result.password,
            "host": result.hostname,
            "port": result.port,
        }

        # Connect to the PostgreSQL database and fetch location IDs
        try:
            conn = psycopg2.connect(**db_params)
            cursor = conn.cursor()

            # Select the location IDs and names from the 'locations' table
            cursor.execute("SELECT location_id, name FROM locations")
            selected_cities = cursor.fetchall()

            self.logger.info(f"Fetched {len(selected_cities)} locations from the database.")

            # Close database connection
            cursor.close()
            conn.close()

            # Loop over the fetched locations and create requests
            for location_id, name in selected_cities:
                url = f"https://uk.trip.com/hotels/list?city={location_id}"
                self.logger.info(f"Scraping URL for city: {name} (ID: {location_id})")
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_hotels,
                    meta={"city_name": name, "location_id": location_id}
                )

        except Exception as e:
            self.logger.error(f"Error fetching locations from database: {e}")

    def parse_hotels(self, response):
        """
        Parses the hotel details from the response.
        """
        city_name = response.meta.get("city_name")
        location_id = response.meta.get("location_id")

        # Extract the JavaScript variable using a regular expression
        script_data = re.search(r'window\.IBU_HOTEL\s*=\s*({.*?});', response.text)

        if script_data:
            # Parse the JSON data
            json_data_str = script_data.group(1)
            self.logger.info(f"Successfully extracted JSON data for city: {city_name} (ID: {location_id})")
            data = json.loads(json_data_str)

            # Extract the hotel list
            hotelList = data.get("initData", {}).get("firstPageList", {}).get("hotelList", [])
            for hotel in hotelList:
                # Extract different sections of hotel details
                hotelBasicInfo = hotel.get("hotelBasicInfo", {})
                commentInfo = hotel.get("commentInfo", {})
                positionInfo = hotel.get("positionInfo", {})
                roomInfo = hotel.get("roomInfo", {})

                # Prepare hotel data
                hotel_data = {
                    "property_title": hotelBasicInfo.get("hotelName", "N/A"),
                    "rating": commentInfo.get("commentScore", "N/A"),
                    "location": positionInfo.get("positionName", "N/A"),
                    "latitude": positionInfo.get("coordinate", {}).get("lat", "N/A"),
                    "longitude": positionInfo.get("coordinate", {}).get("lng", "N/A"),
                    "room_type": roomInfo.get("physicalRoomName", "N/A"),
                    "price": hotelBasicInfo.get("price", "N/A"),
                    "image_url": hotelBasicInfo.get("hotelImg", None),
                    "city_name": city_name,  # Add city name for reference
                    "location_id": location_id,
                }

                if hotel_data.get("image_url") is None:
                    self.logger.warning(f"Missing image for hotel: {hotel_data['property_title']}")
                    continue  # Skip this hotel if no image is available

                # Only yield item if data is valid
                if hotel_data["property_title"] != "N/A":
                    yield hotel_data
                else:
                    self.logger.warning(f"Skipping hotel due to missing data: {hotel_data['property_title']}")

        else:
            self.logger.warning(f"No hotel data found for city: {city_name} (ID: {location_id})")