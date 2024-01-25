import re

def github_crawler(file):
    try:
        main_text = file.read().decode('utf-8')
        
        #\!\[image\] : image tag start
        # \( open
        # \) close
        thumb_nail_url = re.findall(r'\!\[image\]\((.*?)\)', main_text)

        if len(thumb_nail_url) != 0:
            print(thumb_nail_url)

        print(main_text)
        print(thumb_nail_url)
        return ["", main_text, thumb_nail_url[0]]

    except:
        raise AttributeError