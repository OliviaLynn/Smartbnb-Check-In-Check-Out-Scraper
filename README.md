# Smartbnb Check-In/Check-Out Scraper
<img src="https://img.shields.io/badge/python-3.7-blue" /> <img src="https://img.shields.io/badge/selenium-1.141.0-blue" /> <img src="https://img.shields.io/badge/maintained%3F-no-red" /> <img src="https://img.shields.io/github/issues/OliviaLynn/Smartbnb-Check-In-Check-Out-Scraper" /> 

Scrapes all check-in and check-out data from Smartbnb using Selenium.

## Getting Started

These instructions will get the project up and running on your own machine with your own Smartbnb account.

### Prerequisites

#### Selenium (1.141.0)
Our webscraper. Instructions assume you use Chrome, but you can substitute your preferred (selenium-supported) browser instead.
- Install selenium via pip
```shell
pip install selenium
```
- Check what version of Chrome you're using (Chrome menu in the top right > Help > About Google Chrome)
- The Selenium Chromedriver for your version of Chrome can be downloaded [here](https://chromedriver.chromium.org/downloads) (the one in this git is for version 78). Place this exe in the same directory as SmartbnbScraper.py

#### Beautiful Soup (4.7.1)
For parsing the html we scrape.
```shell
pip install beautifulsoup4
```

### Running
From your shell, run the command:
```shell
$ python SmartbnbScraper.py <smartbnb-username> <smartbnb-password>
```
