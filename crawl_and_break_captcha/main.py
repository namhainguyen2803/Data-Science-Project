"""
    Created by @namhainguyen2803 in 25/11/2023
"""
import argparse
import os
from crawl import *
import time

def parse_arguments():
    parser = argparse.ArgumentParser(description='Hello')

    # Add arguments
    parser.add_argument('--start_page', type=int, default=1, help="Lower bound for crawling page index (including)")
    parser.add_argument('--end_page', type=int, default=100000, help="Upper bound for crawling page index (including)")
    parser.add_argument('--data_folder', type=str, default="data", help="Name of data directory")

    args = parser.parse_args()

    return args

if __name__ == "__main__":

    config = vars(parse_arguments())
    START = config["start_page"]
    END = config["end_page"]
    folder_name = config["data_folder"]

    print(f"Page from {START} to {END - 1}, stored in {folder_name} folder")

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    crawler = Crawler()
    for i in range(START, END):
        start_time = time.time()
        crawler.run(i)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")