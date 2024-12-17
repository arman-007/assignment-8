from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from urllib.parse import urlparse
import psycopg2
import os
import scrapy

class HotelsPipeline(ImagesPipeline):

    def get_media_requests(self, item, spider):
        # Download the image
        yield scrapy.Request(item["image_url"], meta={"item": item})

    def file_path(self, request, response=None, info=None, *, item=None):
        # Define the image name
        url_path = urlparse(request.url).path
        return os.path.join("images", os.path.basename(url_path))

    def item_completed(self, results, item, info):
        # Check image download
        image_paths = [x["path"] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Image download failed")

        # Save the hotel data with the image path to the database
        self.save_to_db(item, image_paths[0])
        return item

    def save_to_db(self, item, image_path):
        db_url = os.getenv("DATABASE_URL")
        result = urlparse(db_url)
        db_params = {
            "dbname": result.path.lstrip("/"),
            "user": result.username,
            "password": result.password,
            "host": result.hostname,
            "port": result.port,
        }
        try:
            conn = psycopg2.connect(**db_params)
            cursor = conn.cursor()

            # Create the table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hotels (
                    id SERIAL PRIMARY KEY,
                    property_title TEXT,
                    rating FLOAT,
                    location TEXT,
                    latitude FLOAT,
                    longitude FLOAT,
                    room_type TEXT,
                    price FLOAT,
                    city_name TEXT,
                    image_url TEXT,
                    image_path TEXT
                )
            """)

            # Insert the hotel data
            cursor.execute("""
                INSERT INTO hotels (property_title, rating, location, latitude, longitude, room_type, price, city_name, image_url, image_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                item.get("property_title"),
                item.get("rating"),
                item.get("location"),
                item.get("latitude"),
                item.get("longitude"),
                item.get("room_type"),
                item.get("price"),
                item.get("city_name"),
                item.get("image_url"),
                image_path
            ))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error saving to database: {e}")
