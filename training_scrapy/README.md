# Training Scrapy to crawl data

Training scrapy on springer.com domain to get metrics of journals

## Prequisite

- python v3.x
- pip v3
- mongodb
- requirements.txt file

## Create new Scrapy project

```bash
scrapy startproject training_scrapy
```

Adding requirements.txt file to root directory. Then install module for scrapy:

```bash
pip install -r requirements.txt
```

## Add spider to project

```bash
scrapy genspider springer springer.com
```

## Test and Run 

- Run **srpinger** spider

```bash
scrapy crawl spinger
```

- Render the output to a JSON file

```bash
scrapy crawl spinger -o items.json -t json
```

## Refer

- [Web Scraping and Crawling with Scrapy and MongoDB(2 part)](https://realpython.com/web-scraping-with-scrapy-and-mongodb/)

- [Scrapy Tutorial](https://docs.scrapy.org/en/latest/intro/overview.html)
