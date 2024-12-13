CREATE TABLE IF NOT EXISTS hotels (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    rating FLOAT,
    location TEXT,
    latitude FLOAT,
    longitude FLOAT,
    room_type VARCHAR(255),
    price VARCHAR(50),
    image_paths TEXT
);
