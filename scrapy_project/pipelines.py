# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import os
from sqlalchemy.orm import sessionmaker
from scrapy.pipelines.images import ImagesPipeline
from .models.database import engine
from .models.hotel import Hotel

class HotelPipeline(ImagesPipeline):
    def open_spider(self, spider):
        """
        Called when the spider is opened. Initializes the database session.
        """
        self.Session = sessionmaker(bind=engine)

    def close_spider(self, spider):
        """
        Called when the spider is closed. Closes the database session.
        """
        self.Session.close_all()

    def process_item(self, item, spider):
        """
        Processes each item, saving it to the database.
        """
        session = self.Session()
        try:
            hotel = Hotel(
                title=item['title'],
                rating=item['rating'],
                location=item['location'],
                latitude=item['latitude'],
                longitude=item['longitude'],
                room_type=item['room_type'],
                price=item['price'],
                image_paths=[img['path'] for img in item['images']]
            )
            session.add(hotel)
            session.commit()
        except Exception as e:
            session.rollback()
            spider.logger.error(f"Error saving hotel to database: {e}")
        finally:
            session.close()
        return item

