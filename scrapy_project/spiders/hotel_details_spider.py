import scrapy
import json


class HotelDetailsSpider(scrapy.Spider):
    name = "hotel_details"

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
                meta={"city_name": city["name"]}
            )

    def parse_hotels(self, response):
        # Extract hotel data for the location
        city_name = response.meta["city_name"]
        hotels = response.css(".hotel-card")  # Replace with the correct selector

        for hotel in hotels:
            yield {
                "city_name": city_name,
                "hotel_name": hotel.css(".hotel-name::text").get(),
                "hotel_price": hotel.css(".hotel-price::text").get(),
                "hotel_rating": hotel.css(".hotel-rating::text").get(),
            }
        # pass
