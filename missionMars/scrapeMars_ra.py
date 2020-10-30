#!/usr/bin/env python
# coding: utf-8

# ### Import dependencies
import pandas as pd
import os
import pymongo
import datetime
import json
import requests
import time

from bs4 import BeautifulSoup
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
from pprint import pprint
from url import *

# ### Splinter Module
# 
#     Assign executable path and splinter browser for each web scraping site

# Windows Users - syntax below
# headless means to open browswer to view, set to true will happen behind scene
#executable_path = {'executable_path': 'chromedriver.exe'}
#browser = Browser('chrome', **executable_path, headless=False)

# Mac Users - syntax below
# identify location of chromedriver and store it as a variable
#driverPath = !which chromedriver
# Setup configuration variables to enable Splinter to interact with browser
#executable_path = {'executable_path': driverPath[0]}
#browser = Browser('chrome', **executable_path, headless=False)


# ## Step 1 - Web Scraping
# 
#     URL of page to be scraped
#     Retrieve page with the splinter module
#     Create BeautifulSoup object
#     Print soup with elements of page

# ### NASA Mars News
# 
#     Collect the latest News Title and Paragraph Text 
#     Assign the texts to list of dictionaries called 'news' that can be referenced


def scrape():
    print(url_news)

    # assign executable path and splinter browser
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=True)

    browser.visit(url_news)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    time.sleep(5)
    results = soup.find_all('li', class_="slide")
    time.sleep(5)

    news = []
    for result in results:
        news_title = result.find('div', class_="content_title")
        news_p = result.find('div', class_="article_teaser_body")
        news_i = {}
        news_i['Title'] = news_title.text
        news_i['Article'] = news_p.text
        news.append(news_i)

    #close the browser window
    browser.quit()

    # ### JPL Mars Space Images - Featured Image
    # 
    #     Find the image url for the current Featured Mars Image (full size .jpg)
    #     Assign the url string to a variable called image_url_featured

    print(url_img_featured)

    # assign executable path and splinter browser
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=True)

    browser.visit(url_img_featured)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    time.sleep(2)
    results = soup.find_all('article', class_="carousel_item")
    time.sleep(2)

    # identify image id scraping background image featured on cover site
    # assign to image_url_featured
    tag = str(results[0])
    i1 = tag.find('url')
    i2 = tag.find('jpg')
    i3 = tag.find('PIA')
    bkg_image_url = tag[i1+5:i2+3]
    bkg_image = tag[i3:i2+3]
    i4 = bkg_image.find('-')
    image_id = bkg_image[0:i4]
    image_url_featured = f'https://www.jpl.nasa.gov/spaceimages/images/largesize/{image_id}_hires.jpg'

    #close the browser window
    browser.quit()

    # ### Mars Facts
    # 
    #     Use Pandas to scrape the table containing facts about the planet including Diameter, Mass, etc.
    #     Use Pandas to convert the data to a HTML table string.

    print(url_facts)

    tables = pd.read_html(url_facts)
    df_mars = tables[0]
    df_mars = df_mars.rename(columns = {0: 'Description', 1: 'Mars Facts'})
    df_mars.set_index('Description', inplace=True)

    html_table = df_mars.to_html()

    html_string = '''
    <!DOCTYPE html>
    <html lang="en">
      <head>
          <meta charset="UTF-8">
          <title>Mars Facts</title>
          <link rel="stylesheet" href="static/css/style.css"/>
      </head>
      <body class="factsbody">
        {table}
      </body>
    </html>
    '''

    # OUTPUT AN HTML FILE
    with open('templates/factsMars.html', 'w', encoding="utf8") as f:
        f.write(html_string.format(table=df_mars.to_html(classes='tablestyle')))    

    f.close()    

    # ### Mars Hemispheres
    # 
    #     Retrieve high resolution images for each of Mar's hemispheres.
    #     Use Splinter to click on each of the links to the hemispheres in order to find the image url
    #     Save both the image url string for the full resolution hemisphere image, 
    #         and the Hemisphere title containing the hemisphere name.
    #     Use a Python dictionary to store the data using the keys img_url and title.
    #     Append the dictionary with the image url string and the hemisphere title to a list. 
    #     This list will contain one dictionary for each hemisphere.

    print(url_img_hemisphere)

    # assign executable path and splinter browser
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=True)

    browser.visit(url_img_hemisphere)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    time.sleep(2)
    results = soup.find_all('div', class_="item")
    time.sleep(2)

    mars_hemispheres = []
    for i in range(len(results)):

        item = {}

        tag = results[i].find('a', class_='itemLink product-item')
        tag = str(tag)
        i1 = tag.find('href')+6
        i2 = tag.find('img alt')-3
        item_url = tag[i1:i2]

        title = results[i].find('h3').text
        i3 = title.find('Enhanced')-1
        item_title = title[0:i3]

        item['url'] = item_url
        item['title'] = item_title    

        browser.click_link_by_partial_text(title)        

        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')

        downloads = soup.find_all('div', class_='downloads')
        tag2 = downloads[0].find('a')
        tag2 = str(tag2)
        i4 = tag2.find('href')+6
        i5 = tag2.find('target')-2
        item_img_url = tag2[i4:i5]

        item['img_url'] = item_img_url

        mars_hemispheres.append(item)

        browser.back()  

    #close the browser window
    browser.quit()    

    # ## Step 2 - MongoDB and Flask Application
    # 
    #     Display all of the information that was scraped from the URLs above
    #     Convert this notebook into a Python script called 'scrapeMars_ra.py'
    #         Create function called scrape that will execute all of scraping code from above
    #             Returns one Python dictionary containing all of the scraped data
    #     Create a route called /scrape that will import this script and call scrape function
    #         Store the return value in Mongo as a Python dictionary
    #     Create a root route / that will query Mongo database
    #         Pass the mars data into an HTML template to display the data
    #     Create a template HTML file called index.html that will take the mars data dictionary
    #         Display all of the data in the appropriate HTML elements
    missionMars = {}
    
    missionMars['Featured_image_url'] = image_url_featured
    missionMars['Mars_hemispheres'] = mars_hemispheres

    try:
        missionMars['News'] = news[0]
    except (IndexError):
        newsU = []
        news_u = {}
        news_u['Title'] = "Title unavailable"
        news_u['Article'] = "Paragraph unavailable"
        newsU.append(news_u)
        missionMars['News'] = newsU[0]

    return missionMars






