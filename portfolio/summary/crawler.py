from bs4 import BeautifulSoup
import requests
from .infoList import TAG_DICT

def summary_crawler(url, blog):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")

        if soup :
            title_tag = soup.select_one(TAG_DICT[blog]["title"])
            title = title_tag.find(TAG_DICT[blog]["title_tag"]).text
            print(title)

            main_text_tag = soup.select_one(TAG_DICT[blog]["main_text"])

            thumb_nail_url = main_text_tag.find('img').get("src")
            print(thumb_nail_url)
            
            main_text = ' '.join([tag.text.strip() for tag in main_text_tag.find_all(True)])
            print(main_text)
        else:
            raise AttributeError
    except Exception as e:
        raise AttributeError
    

    #print(soup.prettify())
    #sc-ctqQKy hSyKPP atom-one