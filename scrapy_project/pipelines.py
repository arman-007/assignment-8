import json
import random


# class HotelsPipeline:
#     def process_item(self, item, spider):
#         """
#         Processes each item passed from the spider.
#         Picks 3 random elements from the combined list of inboundCities and outboundCities, retaining all data including recommendHotels.
#         """
#         spider.logger.info("Processing item in pipeline...")

#         # Validate data
#         if "inboundCities" not in item or "outboundCities" not in item:
#             raise ValueError("Missing required data: inboundCities or outboundCities.")

#         # Combine inboundCities and outboundCities
#         all_cities = item.get("inboundCities", []) + item.get("outboundCities", [])

#         # Ensure we have at least one element to process
#         if not all_cities:
#             raise ValueError("No cities found in the data.")

#         # Ensure there are enough cities for random selection
#         if len(all_cities) < 3:
#             raise ValueError("Not enough cities to select 3 randomly.")

#         # Randomly select 3 cities
#         selected_three = []
#         random_selection = random.sample(range(len(all_cities)), 3)

#         for num in random_selection:
#             city = all_cities[num]
#             selected_three.append({
#                 "id": city.get("id"),
#                 "name": city.get("name"),
#                 "count": city.get("count"),
#             })

#         # Pass the tailored data to Scrapy's FEEDS system
#         return {"selectedCities": selected_three}

