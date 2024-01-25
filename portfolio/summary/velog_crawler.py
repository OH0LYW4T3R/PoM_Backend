from bs4 import BeautifulSoup
import requests
from .infoList import TAG_DICT

def velog_crawler(url, blog):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")
        title = ""

        if soup :
            if TAG_DICT[blog]["title"] != None:
                title_tag = soup.select_one(TAG_DICT[blog]["title"])
                title = title_tag.find(TAG_DICT[blog]["title_tag"]).text

            main_text_tag = soup.select_one(TAG_DICT[blog]["main_text"])

            thumb_nail_url = None
            try:
                thumb_nail_url = main_text_tag.find('img').get("src")
                print(thumb_nail_url)
            except:
                pass

            main_text = ' '.join([tag.text.strip() for tag in main_text_tag.find_all(True)])

            print(title)
            print(main_text)
            print(thumb_nail_url)
            return [title, main_text, thumb_nail_url]
        else:
            raise AttributeError
    except:
        raise AttributeError