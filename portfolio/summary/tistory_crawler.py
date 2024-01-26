from bs4 import BeautifulSoup
import requests
from .infoList import TAG_DICT

def tistory_crawler(url, blog):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")

        if soup :
            main_text_tag = (
                soup.select_one(TAG_DICT[blog]["main_text"][0])
                or soup.select_one(TAG_DICT[blog]["main_text"][1])
                or soup.select_one(TAG_DICT[blog]["main_text"][2])
                or soup.select_one(TAG_DICT[blog]["main_text"][3])
            )

            print(main_text_tag)

            thumb_nail_url = None
            try:
                thumb_nail_url = main_text_tag.find('img').get("src")
                print(thumb_nail_url)
            except:
                pass

            main_text = ' '.join([tag for tag in main_text_tag.find_all(text=True)])
            main_text = main_text.replace("\n", "")
            
            print(main_text, thumb_nail_url)
            return ["", main_text, thumb_nail_url]
        else:
            raise AttributeError
    except:
        raise AttributeError