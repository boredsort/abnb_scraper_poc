import logging
import os
import csv
import json
from datetime import datetime

from airbnb_com_crawler import AirBnbComStrategy

output_path = 'output'
target_file = 'target_links.txt'

logger = logging.getLogger()
def execute():
    
    target_file_exists = os.path.exists(target_file)

    if not target_file_exists:
        raise Exception(f'Unable to find target file, name {target_file}')

    target_links = []
    with open(target_file, 'r') as file:
        logger.info('Reading targetfile')
        txt = file.read()
        txt = txt.replace('\n',' ').replace(',',' ')
        target_links = txt.split()

    strategy = AirBnbComStrategy(logger=logger)
    results = []
    for url in target_links:
        crawl_started = str(datetime.now())
        data = strategy.crawl_listing(url)
        crawl_finished = str(datetime.now())
        crawl_data = {
            "url": url,
            "crawl_start": crawl_started ,
            "crawl_finish": crawl_finished,
            "result": data,
        }
        results.append(crawl_data)

        output_dir_exists = os.path.exists(output_path)
        if not output_dir_exists:
            os.makedirs(output_path)
        
        timestamp = int(datetime.timestamp(datetime.now()))

        with open(f'{output_path}/{timestamp}.json', 'w', encoding='UTF-8' ) as file:
            logger.info(f'Writing to file: {timestamp}.json')
            file.write(json.dumps(crawl_data, indent=4))
    
        with open(f'{output_path}/{timestamp}.csv', 'w', encoding='UTF-8',newline='' ) as file:
            logger.info(f'Writing to file: {timestamp}.csv')
            headers = list(data[0].keys())
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)
    execute()