import json
import random
import scrapy
import os
import psycopg2
import logging
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from urllib.parse import urlparse


# class HotelsPipeline:
#     def process_item(self, item, spider):
#         """
#         Processes each item passed from the spider.
#         Picks 3 random elements from the combined list of inboundCities and outboundCities, retaining all data including recommendHotels.
#         """
#         if spider.name == "hotels":
#             spider.logger.info("Processing item in pipeline...")

#             # Validate data
#             if "inboundCities" not in item or "outboundCities" not in item:
#                 raise ValueError("Missing required data: inboundCities or outboundCities.")

#             # Combine inboundCities and outboundCities
#             all_cities = item.get("inboundCities", []) + item.get("outboundCities", [])

#             # Ensure we have at least one element to process
#             if not all_cities:
#                 raise ValueError("No cities found in the data.")

#             # Ensure there are enough cities for random selection
#             if len(all_cities) < 3:
#                 raise ValueError("Not enough cities to select 3 randomly.")

#             # Randomly select 3 cities
#             selected_three = []
#             random_selection = random.sample(range(len(all_cities)), 3)

#             for num in random_selection:
#                 city = all_cities[num]
#                 selected_three.append({
#                     "id": city.get("id"),
#                     "name": city.get("name"),
#                     "count": city.get("count"),
#                 })

#             # Pass the tailored data to Scrapy's FEEDS system
#             return {"selectedCities": selected_three}

class HotelsPipeline:
    def open_spider(self, spider):
        """Initialize the database connection when the spider opens."""
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL is not set in environment variables.")

        # Parse the DATABASE_URL for psycopg2 connection
        from urllib.parse import urlparse

        result = urlparse(db_url)
        self.db_params = {
            "dbname": result.path.lstrip('/'),
            "user": result.username,
            "password": result.password,
            "host": result.hostname,
            "port": result.port,
        }

        try:
            self.conn = psycopg2.connect(**self.db_params)
            self.cursor = self.conn.cursor()
            
            # Create the 'locations' table if it does not exist
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS locations (
                    id SERIAL PRIMARY KEY,
                    location_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    hotel_count INTEGER NOT NULL
                )
            """)
            self.conn.commit()
            spider.logger.info("Database connected and 'locations' table is ready.")

            # Truncate the table to clear any existing records
            self.cursor.execute("TRUNCATE TABLE locations RESTART IDENTITY;")
            self.conn.commit()
            spider.logger.info("Truncated the 'locations' table to clear existing records.")
        except Exception as e:
            spider.logger.error(f"Error connecting to the database: {e}")
            raise

    def close_spider(self, spider):
        """Close the database connection when the spider closes."""
        self.cursor.close()
        self.conn.close()
        spider.logger.info("Database connection closed.")

    def process_item(self, item, spider):
        """
        Processes each item passed from the spider.
        Inserts 3 random cities into the database.
        """
        if spider.name == "hotels":
            spider.logger.info("Processing item in pipeline...")

            # Validate data
            if "inboundCities" not in item or "outboundCities" not in item:
                raise ValueError("Missing required data: inboundCities or outboundCities.")

            # Combine inboundCities and outboundCities
            all_cities = item.get("inboundCities", []) + item.get("outboundCities", [])

            # Ensure we have at least one element to process
            if not all_cities:
                raise ValueError("No cities found in the data.")

            # Ensure there are enough cities for random selection
            if len(all_cities) < 3:
                raise ValueError("Not enough cities to select 3 randomly.")

            # Randomly select 3 cities
            selected_three = []
            random_selection = random.sample(range(len(all_cities)), 3)

            for num in random_selection:
                city = all_cities[num]
                selected_city = {
                    "id": city.get("id"),
                    "name": city.get("name"),
                    "count": city.get("count"),
                }
                selected_three.append(selected_city)

            # Insert selected cities into the database
            try:
                for city in selected_three:
                    self.cursor.execute("""
                        INSERT INTO locations (location_id, name, hotel_count)
                        VALUES (%s, %s, %s)
                    """, (city["id"], city["name"], city["count"]))

                self.conn.commit()
                spider.logger.info(f"Inserted {len(selected_three)} cities into 'locations' table.")
            except Exception as e:
                spider.logger.error(f"Error inserting data into database: {e}")
                self.conn.rollback()

        return item
    

class HotelImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, spider):
        if 'image_url' in item:
            image_url = item['image_url']
            # print(image_url)
            # Passing the item via meta to be accessed later in item_completed
            yield scrapy.Request(image_url, meta={'item': item})

    def file_path(self, request, response=None, info=None, **kwargs):
        # Get image name from the URL (could be customized to use a different naming scheme)
        url_path = urlparse(request.url).path
        image_name = os.path.basename(url_path)
        # print(f"Image will be saved as: {image_name}")
        # Save images in the 'images' directory
        return os.path.join('images', image_name)

    def item_completed(self, results, item, info):
        # Check if the image was downloaded successfully
        image_paths = [x['path'] for ok, x in results if ok]

        if not image_paths:
            raise DropItem("Image download failed")
        
        # Log and save the image path to the database
        image_path = image_paths[0]
        # self.logger.info(f"Image downloaded successfully: {image_path}")

        # Retrieve the item from the meta
        # results[0] is a tuple, so unpack it properly
        for ok, x in results:
            if ok:
                request = x.get('request')
                if request:
                    item = request.meta.get('item')

        # Save the image path to the database
        self.save_hotel_data_to_db(item, image_path)

        return item
    
    def save_hotel_data_to_db(self, item, image_path):
        """Insert hotel data into PostgreSQL database"""
        # Fetch database connection string from environment
        db_url = os.getenv("DATABASE_URL")

        try:
            # Parse the database URL into components
            result = urlparse(db_url)
            db_params = {
                "dbname": result.path.lstrip('/'),
                "user": result.username,
                "password": result.password,
                "host": result.hostname,
                "port": result.port,
            }

            # Connect to PostgreSQL database
            conn = psycopg2.connect(**db_params)
            cursor = conn.cursor()

            # Create the table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hotels (
                    hotel_id SERIAL PRIMARY KEY,
                    property_title TEXT,
                    rating FLOAT,
                    location TEXT,
                    latitude FLOAT,
                    longitude FLOAT,
                    room_type TEXT,
                    price FLOAT,
                    image_url TEXT,
                    image_path TEXT
                )
            """)

            # Insert the hotel data into the table
            cursor.execute("""
                INSERT INTO hotels (property_title, rating, location, latitude, longitude, room_type, price, image_url, image_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                item.get("property_title"),
                item.get("rating"),
                item.get("location"),
                item.get("latitude"),
                item.get("longitude"),
                item.get("room_type"),
                item.get("price"),
                item.get("image_url"),
                image_path
            ))

            # Commit changes and close connection
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error saving hotel data to DB: {e}")