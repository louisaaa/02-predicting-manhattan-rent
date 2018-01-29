import scrapy


class RentSpider(scrapy.Spider):
    name = 'renthop'

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 5,
        "HTTPCACHE_ENABLED": True
    }

    start_urls = [
        'https://www.renthop.com/search/nyc?neighborhoods_str=1&max_price=50000&min_price=0&page=1&sort=hopscore&q=&search=0'
    ]

    def parse(self, response):
        # Extract the links to the individual festival pages
        rental_links = response.xpath('//a[contains(@id, "listing")]/@href').extract()
        #rental_names = response.xpath('//a[contains(@id, "listing")]/text()').extract()
        
        for i in range(len(rental_links)):
            yield scrapy.Request(
                url=rental_links[i],
                callback=self.parse_rental, # defined later
                meta={'url': rental_links[i]}
            )
        #Follow pagination links and repeat
        next_url = 'https://www.renthop.com' + response.xpath('//a[@class="font-blue"]/@href').extract()[-1]

        yield scrapy.Request(
            url=next_url,
            callback=self.parse
        )

    def parse_rental(self, response):
        url = response.request.meta['url']

        #name = response.request.meta['name']
        
        name = (
            response.xpath('//h1[@class="d-none d-lg-block overflow-ellipsis vitals-title"]/text()').extract())

        hop_score = (
            response.xpath('//div[@class="text-right d-inline-block"]/div/text()').extract()[0])

        monthly_rent = (
            response.xpath('//div[@class="text-right d-inline-block"]/div/text()').extract()[2])

        location = (
            #why did i put this here? was not right onw: response.xpath('//div[@class="columns-2"]/div/text()').extract()[0])
            response.xpath('//div[@class="float-none float-lg-left text-center text-lg-left"]/div/text()').extract())

        beds = (
            response.xpath('.//tr/td/text()').extract()[0])

        baths = (
            response.xpath('.//tr/td/text()').extract()[1])

        sq_ft = (
            response.xpath('.//tr/td/text()').extract()[2])
        #or if there is no square feet listed, will be Immediate Move-In I think

        subway_station_distances = (
            response.xpath('//span[@style="color: black; font-weight: bold"]/text()').extract())

        features = (
            response.xpath('//div[@class="columns-2"]/div/text()').extract())
        #returns a list of features like elevator, doorman, etc

        yield {
            'url': url,
            'name': name,
            'hop_score': hop_score,
            'monthly_rent': monthly_rent,
            'location': location,
            'beds': beds,
            'baths': baths,
            'sq_ft': sq_ft,
            'subway_station_distances': subway_station_distances,
            'features': features

        }
