### Hotel Data Scraper
This project is a Scrapy-based web scraper designed to gather hotel data from a specified website. It consists of two spiders that work together to extract hotel locations and details, download images, and store the processed data into a PostgreSQL database.

#### Installation 
1. Cole the repo:
```bash
git clone https://github.com/arman-007/assignment-8.git
cd assignment-8
```

2. Environment Configuration
Create a .env file to store your database connection variables:
```bash
DATABASE_URL=postgresql://myuser:mypassword@db:5432/hotel_db
```

3. Build and Run the Project
```bash
docker-compose up --build
```