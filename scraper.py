# Use bs4 instead of pure string manipulation performance almost definitely doesn't matter much here and in case we want comments in the future
from bs4 import BeautifulSoup
import pandas as pd
import requests
import json
from tqdm import tqdm
import re

base_url = "https://willyoupressthebutton.com"

class SiteData:
    def __init__(self, url):
        self.url = url
        self.res = requests.get(self.url)
        self.data = self.res.text
        self.soup = BeautifulSoup(self.data, 'html.parser')

class PollData:
    def __init__(self, id):
        self.url_data = SiteData(f"{ base_url }/{ id }/stats")
        self.reward = self.url_data.soup.find("div", id="cond").get_text()
        self.consequence = self.url_data.soup.find("div", id="res").get_text()
        self.for_it_percentage = int(re.search("\((\d+(?:\.\d+)?)%\)", self.url_data.soup.find_all("span", {"class": "statsBarLeft"})[0].get_text()).group(1))
        self.against_it_percentage = 100 - self.for_it_percentage
    
    def as_dict(self):
        return {
            "url": self.url_data.url,
            "reward": self.reward,
            "consequence": self.consequence,
            "for_it_percentage": self.for_it_percentage,
            "against_it_percentage": self.against_it_percentage
        }

    def __str__(self):
        return json.dumps(self.as_dict())

scraped_data = []
start = int(input("Start the scraping at: "))
end = int(input("End the scraping before: "))
num_to_search = end - start
for i in tqdm(range(start, end)):
    try:
        scraped_data.append(PollData(i).as_dict())
    except KeyboardInterrupt:
        break # e.g. Ctrl+C
    except:
        pass # Ignore removed or nonexistant polls

df = pd.DataFrame.from_records(scraped_data)
print("Sample:")
print(df)
print(f"{ len(df) / num_to_search * 100 }% were valid polls!")

df.to_csv("data.csv")