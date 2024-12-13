from sqlalchemy import Column, Integer, String, Float, Text
from .database import Base

class Hotel(Base):
    __tablename__ = 'hotels'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    rating = Column(Float, nullable=True)
    location = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    room_type = Column(String, nullable=True)
    price = Column(String, nullable=True)
    image_paths = Column(Text, nullable=True)
