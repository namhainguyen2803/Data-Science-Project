"""
    Created by @namhainguyen2803 in 25/11/2023
"""
import os
from crawl import *
import time



if __name__ == "__main__":

    folder_name = 'data'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    crawler = Crawler()
    crawler.prepare_driver()
    for i in range(1, 10000):
        start_time = time.time()
        crawler.run(i)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")