VERIFIED_BLOG_LIST = set(["velog", "tistory", "github", "notion"])

TAG_DICT = {
    "velog" : {
        "title" : ".head-wrapper",
        "title_tag" : "h1",
        "main_text" : ".sc-ctqQKy" 
    },
    "tistory" : {
        "title" : None,
        "title_tag" : None,
        "main_text" : [
            "div.entry-content", 
            "div.contents_style", 
            "div.article_view", 
            "article"
        ]
    },
    "github" : {
        "title" : None,
        "title_tag" : None,
        "main_text" : "article"
    },
    "notion" : {
        "title" : "header",
        "title_tag" : "h1",
        "main_text": ".page-body"
    }
}
