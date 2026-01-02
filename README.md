# Web-Scraping
Project Overview
Modern websites often load content dynamically, making traditional scraping methods ineffective.
This project addresses that challenge by using Selenium WebDriver to interact with a live website, extract relevant property information, and store it in a structured MySQL database.
The goal is to simulate a real-world data collection pipeline used in analytics, real estate platforms, and automation systems.

Tech Stack
Python
Selenium WebDriver
MySQL
ChromeDriver
webdriver-manager

Key Features
Automated navigation through dynamically rendered webpages
Selection of city and locality using interactive dropdowns
Handling of JavaScript-loaded content and page scroll behavior
Extraction of:
  Property address
  Price
  Price per square foot
Storage of scraped data into a MySQL database
Basic error handling to maintain script stability

Notes & Limitations
The website uses dynamically generated components that may change structure over time.
Some UI elements (dropdowns, filters) are partially dynamic, which can limit full automation.
The scraper is intentionally designed to handle stable, accessible elements only, ensuring reliability and ethical scraping practices.
