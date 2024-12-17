import unittest
from unittest.mock import patch, MagicMock
from scrapy_project.pipelines import HotelsPipeline

class TestHotelsPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = HotelsPipeline()

    @patch("psycopg2.connect")
    def test_save_to_db(self, mock_connect):
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simulate hotel item
        item = {
            "property_title": "Test Hotel",
            "rating": 4.5,
            "location": "Downtown",
            "latitude": 10.1,
            "longitude": 20.2,
            "room_type": "Deluxe",
            "price": 100,
            "city_name": "Test City",
            "image_url": "https://example.com/image.jpg"
        }
        image_path = "images/test_image.jpg"

        # Test database save
        self.pipeline.save_to_db(item, image_path)

        mock_cursor.execute.assert_called()  # Ensure SQL commands were executed
        mock_conn.commit.assert_called_once()  # Ensure transaction was committed
