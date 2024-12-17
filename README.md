

# **Hotel Data Scraper**

This project is a **Scrapy-based web scraper** that gathers hotel data from a specified website. It extracts hotel locations, detailed information (e.g., rating, price, room type), downloads images, and stores the processed data into a **PostgreSQL** database. The project is containerized using **Docker** for easy setup and execution.

---

## **Table of Contents**
1. [Features](#features)  
2. [Setup Instructions](#setup-instructions)  
   - [Clone the Repository](#1-clone-the-repository)  
   - [Environment Configuration](#2-environment-configuration)  
   - [Build and Run the Project](#3-build-and-run-the-project)  
   - [Accessing the Database](#4-accessing-the-database)  
3. [Usage](#usage)  
4. [Testing](#testing)  
5. [Database Access](#database-access)  
6. [Project Structure](#project-structure)  

---

## **Features**

- **Location Scraping**: Randomly selects hotel locations from the website.  
- **Hotel Details Scraping**: Fetches details such as name, rating, location, latitude/longitude, price, and images for hotels.  
- **Image Downloading**: Downloads hotel images and organizes them into a specified folder.  
- **Database Integration**: Stores hotel details and image paths into a **PostgreSQL** database.  
- **Dockerized Deployment**: Simplified setup and execution using Docker.  

---

## **Setup Instructions**

### **1. Clone the Repository**

Start by cloning the project repository:

```bash
git clone https://github.com/arman-007/assignment-8.git
cd assignment-8
```

---

### **2. Environment Configuration**

Create a `.env` file in the root directory to store database connection details:

```bash
DATABASE_URL=postgresql://myuser:mypassword@db:5432/hotel_db
```


---

### **3. Build and Run the Project**

#### **Build the Docker Image**  

Build the project using Docker Compose:

```bash
docker-compose build
```

#### **Start the PostgreSQL Database**

Run the PostgreSQL container in detached mode:

```bash
docker-compose up db -d
```

#### **Run the Web Scraper**

Start the scraper:

```bash
docker-compose up web
```

This will:  
- Start scraping hotel locations and details.  
- Download images to the `images/` folder.  
- Store data into the PostgreSQL database.

---

### **4. Accessing the Database**

To interact with the database, follow these steps:

1. **Enter the Database Container**:

   ```bash
   docker exec -it hotel_scraper_db bash
   ```

2. **Access PostgreSQL**:

   ```bash
   psql -U myuser -d hotel_db
   ```

3. **View Hotel Data**:

   Run the following SQL query to check scraped hotel data:

   ```sql
   SELECT * FROM hotels;
   ```

---

## **Usage**

### **Run the Scraper**
To run the scraper for hotel data:

```bash
docker-compose up web
```

### **Run Unit Tests** (Work in Progress)
Run unit tests for the project:

```bash
docker-compose up tests
```

> **Note**: Unit tests have not been fully implemented yet.

---

## **Testing**

- Tests will be implemented using Python's `unittest` framework.  
- Coverage reports will also be included for code quality analysis.

---

## **Database Access**

### **Direct Interaction**
Once inside the database container, you can run SQL commands directly:

1. Enter the database container:
   ```bash
   docker exec -it hotel_scraper_db bash
   ```

2. Access PostgreSQL:
   ```bash
   psql -U myuser -d hotel_db
   ```

3. Query the tables:
   ```sql
   SELECT * FROM hotels;
   ```

---

## **Project Structure**

The project follows a clean and organized structure:

```
assignment-8/
│
├── Dockerfile                 # Defines the scraper environment
├── docker-compose.yml         # Docker services configuration
├── .env                       # Environment variables for the database
├── hotels_spider.py           # Scrapy spider for scraping hotels
├── pipelines.py               # Pipeline for processing and saving scraped data
├── images/                    # Downloaded hotel images
├── requirements.txt           # Python dependencies
├── tests/                     # Unit test cases (to be implemented)
└── README.md                  # Project documentation
```

---

## **Conclusion**

This project simplifies the task of scraping hotel data, managing images, and integrating with a database. The use of Docker ensures easy deployment, and PostgreSQL stores the data in a reliable and scalable manner.

---