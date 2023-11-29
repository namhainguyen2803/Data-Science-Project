"""
    Created by @namhainguyen2803 in 25/11/2023
"""

import json
import os
import time
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
from bs4 import BeautifulSoup
from lxml import etree
from break_captcha import *
from driver_init import *

TIME = 5


class Crawler:
    def __init__(self):
        self.home_page = "https://alonhadat.com.vn/nha-dat/can-ban/nha-dat/1/ha-noi.html"
        self.root = "https://alonhadat.com.vn"
        self.initialize_captcha_breaker()
        self.initialize_driver()

    def get_pages(self, url):
        """
        Return list of link of all products in the main page
        """
        bs = BeautifulSoup(self.driver.page_source)
        elements = bs.find_all("div", {"class": "ct_title"})
        data = []
        try:
            for feature in elements:
                feature = feature.find_all('a', href=True)
                data.append(feature[0]['href'])
        except Exception as e:
            print(e)
        return [self.root + link for link in data]

    def retrieve_page_index(self, num_page):
        return self.home_page[:-5] + f"/trang--{num_page}.html"

    def retrieve_data(self, url):
        info = {}
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        info['url'] = url
        info['title'] = soup.find("div", class_="title").find_next().text.strip()

        check_description = soup.find_all('div', {'class': 'detail text-content'})
        if len(check_description) > 0:
            info['description'] = check_description[0].text.strip()
        else:
            info['description'] = "nan"

        # info['description'] = soup.find("div", class_="detail text-content").text.strip()

        price = soup.find("span", class_="price")
        if price:
            info['price'] = price.find_next().find_next().text.strip()
        else:
            info['price'] = "nan"

        square = soup.find("span", class_="square")
        if square:
            info['area'] = square.find_next().find_next().text.strip()
        else:
            info['area'] = "nan"

        address = soup.find("div", class_="address")
        if address:
            info['address'] = address.find_next().find_next().text.strip()
        else:
            info['address'] = "nan"

        more_info = soup.find_all("td")
        assert len(more_info) % 2 == 0
        info_list = []
        for x in more_info:
            if x.text != "":
                info_list.append(x.text.strip())
            else:
                check = x.find("img")
                check = check.get("src")
                if check == '/publish/img/check.gif':
                    info_list.append("True")
                else:
                    info_list.append("False")
        for i in range(0, len(info_list) - 1, 2):
            info[info_list[i]] = info_list[i + 1]

        return info

    def initialize_driver(self):
        self.driver = initialize_driver()

    def initialize_captcha_breaker(self):
        self.captcha_breaker = initialize_detector()

    def handle_captcha(self, main_url):
        print(f"URL: {main_url}")
        while True:
            self.driver.get(main_url)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            page = etree.HTML(str(soup))
            message = page.xpath("/html/body/div/div[3]/span[2]")

            if len(message) > 0:  # HANDLE DETECT BOT HERE

                if message[0].text != 'Tôi không phải người máy"':
                    break

                captcha_image = 'cropped_image.png'
                captcha_page_image = 'page_captcha.png'
                captcha_url = self.root + '/' + soup.find('form', id='form1').get('action')
                self.driver.save_screenshot(captcha_page_image)
                img = Image.open(captcha_page_image)
                x1, y1, x2, y2 = 735, 385, 1186, 482
                cropped_img = img.crop((x1, y1, x2, y2))
                cropped_img.save(captcha_image)

                captcha_pred = break_captcha(self.captcha_breaker, captcha_image)
                print(f"Prediction for captcha: {captcha_pred}")
                time.sleep(1)
                self.driver.get(captcha_url)
                self.driver.find_elements("xpath", "//input[@name='captcha']")[0].click()
                self.driver.find_elements("xpath", "//input[@name='captcha']")[0].send_keys(captcha_pred)
                self.driver.find_element("xpath", "//button").click()
                time.sleep(1)
            else:  # not having captcha, break
                break

    def run(self, page_index):
        main_url = self.retrieve_page_index(page_index)

        # try:
        dataset = []

        self.handle_captcha(main_url)

        time.sleep(1)
        list_link_pages = self.get_pages(main_url)
        self.driver.delete_all_cookies()

        for page_link in list_link_pages:
            try:
                self.handle_captcha(page_link)
                data = self.retrieve_data(page_link)
                dataset.append(data)
                self.driver.delete_all_cookies()
            except Exception as e:
                print(e)
        #             print(data)
        if len(dataset) != 0:
            df = pd.DataFrame(dataset)
            df.to_csv(f"data/page_{page_index}.csv", index=False)

        self.driver.delete_all_cookies()