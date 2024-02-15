import logging
import os
import csv
import json
from datetime import datetime

from airbnb_com_crawler import AirBnbComStrategy

output_path = 'output'
target_file = 'target_profiles.json'

logger = logging.getLogger()
def execute():
    
    target_file_exists = os.path.exists(target_file)

    if not target_file_exists:
        raise Exception(f'Unable to find target file, name {target_file}')

    targets = []
    with open(target_file, 'r', encoding='utf-8') as file:
        logger.info(f'[*] Reading targetfile {target_file}')
        targets = json.loads(file.read().replace('\n',' '))

    strategy = AirBnbComStrategy(logger=logger)
    results = []
    for profile in targets.get('profiles',[]):
        url = profile.get('url')
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
            logger.info(f'[*] Writing to file: {timestamp}.json')
            file.write(json.dumps(crawl_data, indent=4))
    
        file_title = '_'.join(profile.get('label','').lower().split()) + f'_{timestamp}'
        with open(f'{output_path}/{file_title}.csv', 'w', encoding='UTF-8',newline='' ) as file:
            logger.info(f'[*] Writing to file: {file_title}.csv')
            headers = list(data[0].keys())
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)
    execute()