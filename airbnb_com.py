
import json
import re
from datetime import datetime

from curl_cffi import requests as c_request
from bs4 import BeautifulSoup


curl_request = c_request

class AirBnbComStrategy:


    def __init__(self, logger=None):
        self.logger=logger

    def crawl_listing(self, url):
        self.logger.info(f'Connecting to: {url}')
        raw_data = download(url)
        self.logger.info(f'Parsing Data')
        result = self.parse(raw_data)

        return result
    
    def parse(self, raw_data):
        results = []
        soup = BeautifulSoup(raw_data, 'lxml')


        deffered_state_json = self.get_deffered_state(soup)
        listing_items_json = self.get_listing_items(deffered_state_json)
        try:
            for item in listing_items_json:
                title = self.get_title(item)
                description = self.get_description(item)
                price_per_night = self.get_price_per_night(item)
                # orig_price_per_night = get_orig_price_per_night(item)
                total_price = self.get_total_price(item)
                rating_score = self.get_rating_score(item)
                rating_count = self.get_rating_count(item)
                labels = self.get_labels(item)
                image_url = self.get_image_url(item)

                data = {
                    "title": title,
                    "description": description,
                    "price_per_night": price_per_night,
                    # "original_list_price": orig_price_per_night,
                    "total_price": total_price,
                    "rating_score": rating_score,
                    "rating_count": rating_count,
                    "labels": labels,
                    "image_url": image_url 
                }

                results.append(data)
        except:
            pass
        return results

    def get_title(self, item_json):
        value = str()
        try:
            txt = item_json.get('listing', {}).get('title')
            if txt:
                return txt.strip()
        except:
            pass
        return value

    def get_description(self, item_json):
        value = str()
        try:
            txt = item_json.get('listing', {}).get('name')
            if txt:
                return txt.strip()
        except:
            pass
        return value

    def get_price_per_night(self, item_json):
        value = float()
        try:
            price_displays = item_json.get('pricingQuote', {}).get('structuredStayDisplayPrice')
            if price_displays:
                price_txt = price_displays.get('primaryLine', {}).get('price')
                if price_txt:
                    value = float(re.sub('[^0-9.]', '', price_txt))
        except:
            pass
        return value

    def get_total_price(self, item_json):
        value = float()
        try:
            price_displays = item_json.get('pricingQuote', {}).get('structuredStayDisplayPrice')
            if price_displays:
                price_txt = price_displays.get('secondaryLine', {}).get('price')
                if price_txt:
                    value = float(re.sub('[^0-9.]', '', price_txt))

        except:
            pass
        return value

    def get_rating_score(self, item_json):
        value = float()
        try:
            label_txt = item_json.get('listing', {}).get('avgRatingA11yLabel')
            matches = re.search(r'([0-9.]+) out', label_txt)
            if matches:
                return float(matches.group(1))
        except:
            pass
        return value

    def get_rating_count(self, item_json):
        value = int()
        try:
            label_txt = item_json.get('listing', {}).get('avgRatingA11yLabel')
            matches = re.search(r'(\d+) reviews', label_txt)
            if matches:
                return int(matches.group(1))
        except:
            pass
        return value


    def get_image_url(self, item_json):
        value = str()
        try:
            images = item_json.get('listing', {}).get('contextualPictures',[])
            if images:
                url = images[0].get('picture')
                if url:
                    return url
        except:
            pass
        return value

    def get_labels(self, item_json):
        value = []
        try:
            badges = item_json.get('listing', {}).get('formattedBadges',[])
            if badges:
                for badge in badges:
                    txt = badge.get('text')
                    if txt:
                        value.append(txt.strip())
        except:
            pass
        return value
    
    def get_deffered_state(self, soup):
        tag = soup.select_one('[id="data-deferred-state"]')
        try:
            if tag:
                txt = tag.get_text().strip()
                return json.loads(txt)
        except:
            pass
        return {}

    def get_listing_items(self, deffered_state_json):
        client_data = deffered_state_json.get('niobeMinimalClientData')
        try:
            if client_data:
                search_result = client_data[0][1]
                if search_result:
                    presentation = search_result.get('data', {}).get('presentation', {})
                    if presentation:
                        return presentation.get('staysSearch', {}).get('results', {}).get('searchResults', [])
        except:
            pass
        return []

def download(url):


    headers = {
        'authority': 'www.airbnb.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'viewport-width': '1920',
    }
    
    response = curl_request.get(url, headers=headers, impersonate='chrome110')
    if response and response.status_code in [200, 201]:
        return response.text

    return None


# if __name__ == '__main__':


#     url = 'https://www.airbnb.com/s/Miami--Florida--United-States/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-03-01&monthly_length=3&monthly_end_date=2024-06-01&price_filter_input_type=0&channel=EXPLORE&query=Miami%2C%20Florida%2C%20United%20States&place_id=ChIJEcHIDqKw2YgRZU-t3XHylv8&date_picker_type=calendar&checkin=2024-02-12&checkout=2024-02-13&source=structured_search_input_header&search_type=user_map_move&price_filter_num_nights=1&ne_lat=25.937624991861206&ne_lng=-79.96087820531693&sw_lat=25.537208029404738&sw_lng=-80.39972361725575&zoom=10.95386396617367&zoom_level=10.95386396617367&search_by_map=true'
#     result = crawl_listing(url)

#     print(result)
#     curr_dt = datetime.now()
#     timestamp = int(round(curr_dt.timestamp()))

