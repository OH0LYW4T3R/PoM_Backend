from bs4 import BeautifulSoup
import requests
from .infoList import TAG_DICT

CHUNK_SIZE = 40000

def notion_summary(file):
    try:
        blog = "notion"
        soup = ""
        main_text = ""

        while True:
            chunk = file.read(CHUNK_SIZE)
            if not chunk:
                break
            soup = BeautifulSoup(chunk, "html.parser")
            
            if soup :
                if TAG_DICT[blog]["title"] != None: 
                    title_tag = soup.find(TAG_DICT[blog]["title"])
                    
                    if title_tag:
                        title = title_tag.find(TAG_DICT[blog]["title_tag"]).text
                        print(title)
                    else:
                        pass

                    main_text_tag = soup.select_one(TAG_DICT[blog]["main_text"])

                    if main_text_tag:
                        main_text = main_text.join([tag.text.strip() for tag in main_text_tag.find_all(True)])
                        print(main_text)

    except:
        raise AttributeError
    