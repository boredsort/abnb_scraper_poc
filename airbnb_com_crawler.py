
import json
import re
from datetime import datetime
from urllib.parse import urlencode, quote

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
            rank = 1
            for item in listing_items_json:
                url = self.get_url(item)
                room_data = self.fetch_room_data(url)
                title = self.get_title(item)
                description = self.get_description(item)
                price_per_night = self.get_price_per_night(item)
                orig_price_per_night = self.get_orig_price_per_night(item)
                total_price = self.get_total_price(item)
                rating_score = self.get_rating_score(item)
                rating_count = self.get_rating_count(item)
                labels = self.get_labels(item)
                image_url = self.get_image_url(item)
                host_name = self.get_pdp_host_name(room_data)
                cleanliness = self.get_pdp_clean(room_data)
                accuracy = self.get_pdp_clean(room_data)
                communication = self.get_pdp_communication(room_data)
                location_rate = self.get_pdp_location_rating(room_data)
                check_in = self.get_pdp_check_in(room_data)
                guest_capacity = self.get_pdp_capacity(room_data)
                lat = self.get_pdp_lat(room_data)
                lon = self.get_pdp_lon(room_data)
                baths = self.get_pdp_baths(room_data)
                # guests = self.get_pdp_guests(room_data)
                data = {
                    "rank": rank,
                    "title": title,
                    "url": url,
                    "description": description,
                    "price_per_night": price_per_night,
                    "original_price_per_night": orig_price_per_night,
                    "total_price": total_price,
                    "rating_score": rating_score,
                    "rating_count": rating_count,
                    "labels": labels,
                    "image_url": image_url,
                    "host_name": host_name,
                    "cleanliness" : cleanliness,
                    "accuracy": accuracy,
                    "location_rate": location_rate,
                    "communication": communication,
                    "check_in": check_in,
                    "guest": guest_capacity,
                    'lattitude': lat,
                    'longtitude': lon
                    # "baths": baths
                }
                rank += 1
                results.append(data)
        except:
            pass
        return results
    
    def get_url(self, item_json):
        value = str()
        try:
            base_url = 'https://www.airbnb.com/rooms/'
            id = item_json.get('listing', {}).get('id')
            if id:
                value = f'{base_url}{id.strip()}'
        except:
            pass
        return value

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
                price_txt = price_displays.get('primaryLine', {}).get('price','')
                if not price_txt:
                    price_txt = price_displays.get('primaryLine', {}).get('discountedPrice')
                if price_txt:
                    value = float(re.sub('[^0-9.]', '', price_txt))
        except:
            pass
        return value
    
    def get_orig_price_per_night(self, item_json):
        value = float()
        try:
            price_displays = item_json.get('pricingQuote', {}).get('structuredStayDisplayPrice')
            if price_displays:
                price_txt = price_displays.get('primaryLine', {}).get('originalPrice')
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
    
    def get_pdp_js_link(self, soup):
        tag = soup.find('script', src=re.compile('web/common/frontend/gp-stays-pdp-route/routes/PdpPlatformRoute.prepare', re.IGNORECASE))
        if tag:
            return tag.get('src')
        return None

    def fetch_room_data(self, url):

        try:
            print(f'[*] Fetching PDP data {url}')
            raw = download(url)
            if raw:
                soup = BeautifulSoup(raw, 'lxml')
                pdp_link = self.get_pdp_js_link(soup)
                if pdp_link:
                    operation_id = self.fetch_pdp_operation_id(pdp_link)
                    if operation_id:
                        pdp_api_url = self.generate_pdp_api_url(soup, operation_id)
                        pdp_api_header = self.generate_pdp_api_headers(soup, url)
                        pdp_raw = download(pdp_api_url, headers=pdp_api_header)
                        if pdp_raw:
                            pdp_json = json.loads(pdp_raw)
                            room_data = pdp_json.get('data', {}).get('presentation', {}).get('stayProductDetailPage', {})
                            if room_data:
                                return room_data

        except:
            pass
        return {}
    
    def fetch_pdp_operation_id(self, url):
        try:
            raw = download(url)
            if raw:
                matches = re.search(r"'StaysPdpSections',type:'query',operationId:'([0-9a-zA-Z]+)'", raw)
                if matches:
                    return matches.group(1)
        except:
            pass
        return None
    
    def get_injector_instance_json(self, soup):
        try:
            tag = soup.select_one('#data-injector-instances')
            if tag:
                txt = tag.get_text().strip()
                return json.loads(txt)
        except:
            pass
        return {}

    def generate_pdp_api_url(self, soup, operation_id):
        injector_json = self.get_injector_instance_json(soup)
        spa_data = injector_json.get('root > core-guest-spa', {})
        try:
            if spa_data:
                client_data = spa_data[1][1]
                niobe_data = client_data.get('niobeMinimalClientData',[None])[0][0]

                variables = niobe_data.replace('StaysPdpSections:','')
                extensions = json.dumps({"persistedQuery":{"version":1,"sha256Hash":operation_id}},separators=(',',':'))
                query_params = {
                    "operationName": "StaysPdpSections",
                    "locale": "en",
                    "currency": "CAD",
                    "variables": variables,
                    "extensions": extensions
                }
                return f'https://www.airbnb.com/api/v3/StaysPdpSections/{operation_id}?{urlencode(query_params, quote_via=quote)}'
        except:
            pass

        return None
    
    def generate_pdp_api_headers(self, soup, pdp_url):
        header = {}
        try:
            injector_json = self.get_injector_instance_json(soup)
            spa_data = injector_json.get('root > core-guest-spa', {})
            bootstrap_token_data= spa_data[0][1]
            api_key = bootstrap_token_data.get('layout-init', {}).get('api_config', {}).get('key')
            header = {
                "authority":"www.airbnb.com",
                "accept":"*/*",
                "accept-language":"en-US,en;q=0.9",
                "content-type":"application/json",
                "referer": pdp_url,
                "sec-fetch-dest":"empty",
                "sec-fetch-mode":"cors",
                "sec-fetch-site":"same-origin",
                "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "x-airbnb-api-key":api_key,
                "x-airbnb-graphql-platform":"web",
                "x-airbnb-graphql-platform-client":"minimalist-niobe",
                "x-airbnb-supports-airlock-v2":"true",
                "x-csrf-token":"null",
                "x-csrf-without-token":"1",
                "x-niobe-short-circuited":"true"
            }
        except:
            print('failed to generate api headers')
        return header

    def get_pdp_host_name(self, room_data):
        value = str()
        try:
            sbui_data = room_data.get('sections', {}).get('sbuiData')
            if sbui_data:
                sections = sbui_data.get('sectionConfiguration', {}).get('root', {}).get('sections',[])
                for section in sections:
                    if section.get('sectionId') == 'HOST_OVERVIEW_DEFAULT':
                        sec_data = section.get('sectionData')
                        title = sec_data.get('title')
                        if title:
                            value = title.replace('Hosted by','').strip()
        except:
            pass
        return value


    def get_pdp_clean(self, room_data):
        value = float()
        try:
            meta_data = room_data.get('sections', {}).get('metadata')
            if meta_data:
                event_data = meta_data.get('loggingContext', {}).get('eventDataLogging')
                rate = event_data.get('cleanlinessRating', 0)
                if rate:
                    value = rate
        except:
            pass
        return value
    def get_pdp_communication(self, room_data):
        value = float()
        try:
            meta_data = room_data.get('sections', {}).get('metadata')
            if meta_data:
                event_data = meta_data.get('loggingContext', {}).get('eventDataLogging')
                rate = event_data.get('communicationRating', 0)
                if rate:
                    value = rate
        except:
            pass
        return value
    def get_pdp_location_rating(self, room_data):
        value = float()
        try:
            meta_data = room_data.get('sections', {}).get('metadata')
            if meta_data:
                event_data = meta_data.get('loggingContext', {}).get('eventDataLogging')
                rate = event_data.get('locationRating', 0)
                if rate:
                    value = rate
        except:
            pass
        return value
    def get_pdp_check_in(self, room_data):
        value = float()
        try:
            meta_data = room_data.get('sections', {}).get('metadata')
            if meta_data:
                event_data = meta_data.get('loggingContext', {}).get('eventDataLogging')
                rate = event_data.get('checkinRating', 0)
                if rate:
                    value = rate
        except:
            pass
        return value
    def get_pdp_lat(self, room_data):
        value = str()
        try:
            meta_data = room_data.get('sections', {}).get('metadata')
            if meta_data:
                event_data = meta_data.get('loggingContext', {}).get('eventDataLogging')
                lat = event_data.get('listingLat', 0)
                if lat:
                    value = str(lat)
        except:
            pass
        return value
    
    def get_pdp_lon(self, room_data):
        value = str()
        try:
            meta_data = room_data.get('sections', {}).get('metadata')
            if meta_data:
                event_data = meta_data.get('loggingContext', {}).get('eventDataLogging')
                lon = event_data.get('listingLng', 0)
                if lon:
                    value = str(lon)
        except:
            pass
        return value

    def get_pdp_capacity(self, room_data):
        value = int()
        try:
            meta_data = room_data.get('sections', {}).get('metadata')
            if meta_data:
                capacity = meta_data.get('sharingConfig', {}).get('personCapacity')
                if capacity:
                    value = capacity
        except:
            pass
        return value
    
    def get_pdp_baths(self, room_data):
        value = int()
        try:
            sbui_data = room_data.get('sections', {}).get('sbuiData')
            if sbui_data:
                sections = sbui_data.get('sectionConfiguration', {}).get('root', {}).get('sections',[])
                for section in sections:
                    if section.get('sectionId') == 'OVERVIEW_DEFAULT_V2':
                        sec_data = section.get('sectionData')
        except:
            pass
        return value
    # def get_pdp_guests(room_data):
    #     pass



def download(url, headers={}):

    if not headers:
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
