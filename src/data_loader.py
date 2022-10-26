import requests
import gzip
import io
import pandas as pd
from pathlib import Path

class Data:
    def __init__(self, listings, calendars, reviews):
        self.listings = listings
        self.calendars = calendars
        self.reviews = reviews

class DataLoader:  
    def __init__(self, cfg):
        self.log_tag = "[Dataloader]"
        self.verbose = cfg.verbose
        self.city = cfg.city.lower()

        # Cache data locally on disk to avoid network requests.
        self.cache = PersistentCache(self.city, self.verbose)

        print(f"{self.log_tag}: Data target: '{self.city}'.")

  
    def load(self) -> Data:
        print(f"{self.log_tag}: Loading data.")
        data = self.cache.load()

        if data is None:
            data = self.load_from_network()
            self.cache.save(data)

        assert data is not None, f"{self.log_tag}: ERROR: Could not load data."

        if self.verbose:
            print(f"{self.log_tag}: Loaded {len(data.listings)} listings")
            print(f"{self.log_tag}: Loaded {len(data.calendars)} calendar entries")
            print(f"{self.log_tag}: Loaded {len(data.reviews)} reviews")

        return data


    def load_from_network(self) -> Data or None:
        gateway_url = get_gateway_url_from_city(self.city)

        if self.verbose:
            print(f"{self.log_tag}: Loading from network.")
            print(f"{self.log_tag}: Gateway URL: '{gateway_url}'.")

        page_data_request = requests.get(gateway_url)

        if page_data_request.status_code != 200:
            print(f"{self.log_tag}: ERROR: Could not load data from network.")
            print(f"{self.log_tag}: Status code: {page_data_request.status_code}")
            print(f"{self.log_tag}: Response: {page_data_request.text}")
            return None

        page_data = page_data_request.json()
        
        listings_url: str = page_data["result"]["pageContext"]["listingsData"]

        # Change 'visualisations' to 'data' to be compliant with the other csv file urls
        listings_url = listings_url.replace("visualisations", "data")

        # Use the listing urls and change it for calendars and reviews.
        calendar_url = listings_url.replace("listings", "calendar")
        reviews_url = listings_url.replace("listings", "reviews")

        if self.verbose:
            print(f"{self.log_tag}: Listings URL: '{listings_url}'")
            print(f"{self.log_tag}: Calendar URL: '{calendar_url}'")
            print(f"{self.log_tag}: Reviews URL: '{reviews_url}'")

        listings_data = self.download_and_unzip_data("listings", listings_url)
        calendars_data = self.download_and_unzip_data("calendars", calendar_url)
        reviews_data = self.download_and_unzip_data("reviews", reviews_url)

        return Data(listings_data, calendars_data, reviews_data)

    def download_and_unzip_data(self, tag: str, url: str):
        if self.verbose:
            print(f"{self.log_tag}: Downloading {tag}.")

        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with gzip.open(io.BytesIO(r.content)) as f:
                text = f.read()
                return pd.read_csv(io.BytesIO(text))

        

class PersistentCache:
    def __init__(self, city: str, verbose: bool):
        self.log_tag = "[PersistentCache]"
        self.verbose = verbose
        self.city = city
        self.cache_directory = Path(f"../downloaded_data/{city}")

    def load(self):
        if self.verbose:
            print(f"{self.log_tag}: Loading from cache.")

        if not self.cache_directory.exists():
            if self.verbose:
                print(f"{self.log_tag}: Cache miss.")
            return None
            
        listings = pd.read_csv(f"{self.cache_directory}/listings.csv")
        calendars = pd.read_csv(f"{self.cache_directory}/calendars.csv")
        reviews = pd.read_csv(f"{self.cache_directory}/reviews.csv")
        
        return Data(listings, calendars, reviews)

    def save(self, data: Data):
        if self.verbose:
            print(f"{self.log_tag}: Caching data in '{self.cache_directory}'.")

        self.cache_directory.mkdir(parents=True, exist_ok=True)

        data.listings.to_csv(f"{self.cache_directory}/listings.csv", index=False)
        data.calendars.to_csv(f"{self.cache_directory}/calendars.csv", index=False)
        data.reviews.to_csv(f"{self.cache_directory}/reviews.csv", index=False)




def get_gateway_url_from_city(city: str) -> str:
    return f'http://insideairbnb.com/page-data/{city}/page-data.json'