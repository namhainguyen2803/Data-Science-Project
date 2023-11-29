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

    def retrieve_data(self, page_source):
        data = {}
        bs = BeautifulSoup(page_source)
        page = etree.HTML(str(bs))

        price = page.xpath("""//*[@id="left"]/div[1]/div[3]/span[1]/span[2]""")[0].text
        price = price.replace(",", ".")
        data['price'] = price

        # get area
        area = page.xpath("""//*[@id="left"]/div[1]/div[3]/span[2]/span[2]""")[0].text
        data['area'] = area

        # get address
        address = page.xpath("""//*[@id="left"]/div[1]/div[4]/span[2]""")[0].text
        address = address.replace(",", ".")
        data['address'] = address

        # get table information
        list_attributes = ['Mã tin', 'Hướng', 'Phòng ăn', 'Loại tin', 'Đường trước nhà',
                           'Nhà bếp', 'Loại BDS', 'Pháp lý', 'Sân thượng', 'Chiều ngang',
                           'Số lầu', 'Chổ để xe hơi', 'Chiều dài', 'Số phòng ngủ', 'Chính chủ', 'Thuộc dự án']

        table = bs.find_all('div', {'class': 'infor'})[0]
        tr_instances = table.find_all('tr')

        for i in range(len(tr_instances)):
            td_instances = tr_instances[i].find_all('td')

            for i in range(len(td_instances)):
                element = td_instances[i].text
                if element in list_attributes:
                    if td_instances[i + 1].find('img'):
                        link_img = td_instances[i + 1].find('img')['src']
                        if "check" in link_img:
                            data[element] = "yes"
                        else:
                            data[element] = "no"
                    else:
                        if '_' in td_instances[i + 1].text or '-' in td_instances[i + 1].text:
                            data[element] = "null"
                        else:
                            data[element] = td_instances[i + 1].text

        # get description
        description = bs.find_all('div', {'class': 'detail text-content'})[0].text
        data['description'] = description

        return data

    def prepare_driver(self):
        self.driver = initialize_driver()

    def run(self, page_index):
        main_url = self.retrieve_page_index(page_index)

        if os.path.exists("data/index.json"):  # index
            with open("data/index.json") as f:
                index = set(json.load(f))
        else:
            index = set()

        try:
            dataset = []
            self.driver.get(main_url)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            check_captcha = soup.find('img', {'class': 'captchagenerator'})

            if check_captcha:  # HANDLE DETECT BOT HERE
                captcha_image = 'cropped_image.png'
                captcha_page_image = 'page_captcha.png'

                captcha_url = self.root + '/' + soup.find('form', id='form1').get('action')
                self.driver.save_screenshot(captcha_page_image)

                img = Image.open('page_captcha.png')
                x1, y1, x2, y2 = 734, 368, 1186, 468
                cropped_img = img.crop((x1, y1, x2, y2))
                cropped_img.save(captcha_image)

                src_link = self.root + check_captcha.get('src')
                print(f"Found captcha, src link: {captcha_url, src_link}")
                captcha_pred = break_captcha(captcha_image)
                print(f"Prediction for captcha: {captcha_pred}")
                time.sleep(1)

                self.driver.get(captcha_url)
                self.driver.find_elements("xpath", "//input[@name='captcha']")[0].click()
                self.driver.find_elements("xpath", "//input[@name='captcha']")[0].send_keys(captcha_pred)
                self.driver.find_element("xpath", "//button").click()
                time.sleep(1)

                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                re_check_captcha = soup.find('img', {'class': 'captchagenerator'})

                if re_check_captcha:
                    print("Failed to break captcha")
                else:
                    print("Successful to break captcha")

            time.sleep(5)
            list_link_pages = self.get_pages(main_url)
            self.driver.delete_all_cookies()

            for page_link in list_link_pages:

                self.driver.get(page_link)
                data = self.retrieve_data(self.driver.page_source)
                if data["Mã tin"] not in index:
                    dataset.append(data)
                    index.add(data["Mã tin"])
                self.driver.delete_all_cookies()
                print(data)
            if len(dataset) != 0:
                df = pd.DataFrame(dataset)
                df.to_csv(f"data/page_{page_index}.csv", index=False)

            with open("data/index.json", "w") as f:
                json.dump(list(index), f)
            self.driver.delete_all_cookies()

        except Exception as e:
            print(e)
