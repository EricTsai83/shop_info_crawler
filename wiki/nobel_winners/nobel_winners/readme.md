# Setting Up Scrapy
[**Reference**](https://github.com/Kyrand/dataviz-with-python-and-js/tree/master/Ch06_Heavyweight_Scraping_with_Scrapy)

Scrapy should be one of the Anaconda packages. If you don't have one, just install it. 

## In Terminal
```
cd youProjectPath
```
```
scrapy startproject nobel_winners
```

## Let’s take a look at the project’s directory tree
```nobel_winners
├── nobel_winners
│ ├── __init__.py
│ ├── items.py
│ ├── pipelines.py
│ ├── settings.py
│ └── spiders
│ └── __init__.py
└── scrapy.cfg
```
>As shown, the project directory has a subdirectory with the same name and a config file scrapy.cfg. The nobel_winners subdirectory is a Python module (containing an __init__.py file) with a few skeleton files and a spiders directory, which will contain your scrapers.

## Spiders process function
Spiders are subclassed scrapy.Spider classes, and any placed in the
`spiders directory` will be automatically detected by Scrapy and made
accessible by name to the scrapy command.

Note: Spider's name call in terminal will remove _spide.py automatilly. You can check completed spider's name in terminal

## Activate in terminal 
1. First navigate to the nobel_winners root directory (containing the scrapy.cfg file) of the scraping project.
2. Checking completed spider's name in terminal.<br>Commend: `scrapy list`
3. To start it scraping, we use the crawl command and direct the output to a filename.json file.<br>Commend: `scrapy crawl Spider_name -o file_name.json`




