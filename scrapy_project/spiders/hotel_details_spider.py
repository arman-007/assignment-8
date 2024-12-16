import scrapy
import json
import re


class HotelDetailsSpider(scrapy.Spider):
    name = "hotel_details"
    custom_settings = {
        'FEED_URI': 'output/hotel_details.json',
    }

    def start_requests(self):
        # Load the selected cities from the first spider's output
        with open("random_3_hotels.json", "r") as f:
            data = json.load(f)



        # Access the first element of the list and get "selectedCities"
        if isinstance(data, list) and len(data) > 0:
            selected_cities = data[0].get("selectedCities", [])
        else:
            self.logger.error("Invalid JSON structure in random_3_hotels.json")
            return
        # print(selected_cities)
        self.logger.info(f"Selected cities: {selected_cities}")

        for city in selected_cities:
            location_id = city["id"]
            url = f"https://uk.trip.com/hotels/list?city={location_id}"
            yield scrapy.Request(
                url=url,
                callback=self.parse_hotels,
                # meta={"city_name": city["name"]}
            )
            # print(response)

    def parse_hotels(self, response):
        # Extract the JavaScript variable using a regular expression
        script_data = re.search(r'window\.IBU_HOTEL\s*=\s*({.*?});', response.text)
        # print(response.text)

        if script_data:
            # Parse the JSON data
            json_data_str = script_data.group(1)
            self.logger.info("Successfully extracted JSON data from window.IBU_HOTEL.")
            data = json.loads(json_data_str)

        hotelList = data.get("initData", {}).get("firstPageList", {}).get("hotelList", {})
        # print(len(hotelList))
        for hotel in hotelList:
            # different sections of each hotels
            hotelBasicInfo = hotel.get("hotelBasicInfo", {})
            commentInfo = hotel.get("commentInfo", {})
            positionInfo = hotel.get("positionInfo", {})
            roomInfo = hotel.get("roomInfo", {})
            # print(hotel)

            hotel_data = {
                "property_title" : hotelBasicInfo.get("hotelName", "N/A"),
                "rating" : commentInfo.get("commentScore", "N/A"),
                "location" : positionInfo.get("positionName", "N/A"),
                "latitude" : positionInfo.get("coordinate", {}).get("lat", "N/A"),
                "longitude" : positionInfo.get("coordinate", {}).get("lng", "N/A"),
                "room_type" : roomInfo.get("physicalRoomName", "N/A"),
                "price" : hotelBasicInfo.get("price", "N/A"),
                "image_url" : hotelBasicInfo.get("hotelImg", None)
            }
            if hotel_data.get("image_url") is None:
                self.logger.warning(f"Missing image for hotel: {hotel_data['property_title']}")
                continue  # Skip this hotel if no image is available

            # Only yield item if data is valid
            if hotel_data["property_title"] != "N/A":
                yield hotel_data
            else:
                self.logger.warning(f"Skipping hotel due to missing data: {hotel_data['property_title']}")