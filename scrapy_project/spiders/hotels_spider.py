import scrapy
import json
import re


class HotelsSpider(scrapy.Spider):
    name = "hotels"
    # custom_settings = {
    #     'FEED_URI': './random_3_hotels.json',
    # }
    start_urls = [
        'https://uk.trip.com/hotels/?locale=en-GB&curr=GBP'
    ]

    def parse(self, response):
        """
        Extracts the JSON data stored in window.IBU_HOTEL and passes it to the pipeline.
        """
        self.logger.info("Parsing the response to extract JSON data from window.IBU_HOTEL...")

        # Extract the JavaScript variable using a regular expression
        script_data = re.search(r'window\.IBU_HOTEL\s*=\s*({.*?});', response.text)

        if script_data:
            # Parse the JSON data
            json_data_str = script_data.group(1)
            self.logger.info("Successfully extracted JSON data from window.IBU_HOTEL.")
            data = json.loads(json_data_str)

            # Navigate to the required lists
            htls_data = data.get("initData", {}).get("htlsData", {})
            inbound_cities = htls_data.get("inboundCities", [])
            outbound_cities = htls_data.get("outboundCities", [])

            # Yield raw data to the pipeline
            yield {
                "inboundCities": inbound_cities,
                "outboundCities": outbound_cities,
            }
        else:
            self.logger.warning("Could not find window.IBU_HOTEL in the response.")
