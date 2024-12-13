import scrapy


class HotelsSpider(scrapy.Spider):
    name = "hotels"
    start_urls = [
        'https://uk.trip.com/hotels/?locale=en-GB&curr=GBP'
    ]

    def start_requests(self):
        """
        Initiates requests to the specified URLs with Playwright enabled.
        """
        self.logger.info("Starting requests to scrape hotels from the specified URLs.")
        for url in self.start_urls:
            self.logger.info(f"Initiating request to {url}")
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_context": "new",  # Use a new context for the browser
                    "playwright_include_page": True,
                },
                callback=self.parse,
                errback=self.handle_error
            )

    async def parse(self, response):
        """
        Parses the response to extract hotel data.
        """
        self.logger.info("Parsing the response...")
        page = response.meta.get("playwright_page")  # Access Playwright's page object

        # Wait for a specific selector to ensure content has loaded
        await page.wait_for_selector("ul.m-swiper_list")
        hotels = response.css('ul.m-swiper_list > li.m-swiper_itemWrap')

        if not hotels:
            self.logger.warning("No hotels found in the response. Verify the CSS selector or the page content.")

        for hotel in hotels:
            name = hotel.css('div.recommend-hotelcard_name::text').get()
            hotel_count = hotel.css('div.recommend-hotelcard_count::text').get()
            image_url = hotel.css('div.m-lazyImg__img::attr(src)').get()
            link = hotel.css('a::attr(href)').get()

            self.logger.debug(f"Extracted Hotel: {name}, Count: {hotel_count}, Image URL: {image_url}, Link: {link}")

            yield {
                'name': name,
                'hotel_count': hotel_count,
                'image_url': image_url,
                'link': link,
            }

        # Close the Playwright page to release resources
        await page.close()

    def handle_error(self, failure):
        """
        Handle errors and log useful debug information.
        """
        self.logger.error(f"Request failed with error: {failure.value}")
        self.logger.debug(f"Failure traceback: {failure.getTraceback()}")
