import logging


OUTPUT_DIR = "./output"
TEMP_DIR = "./output/tmp"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"

DOAMINS_TEXT_SELECTORS =  {
    "ynet.co.il": {
        "selectors": {
            "headline": "h1.mainTitle",
            "description": "h2 span",
            "body": "#ArticleBodyComponent",
            "author": "",
            "date": "",
        },
    },
    "walla.co.il": {
        "selectors": {
            "headline": "h1.title",
            "description": "h2.subtitle",
            "body": ".article-content",
            "author": "",
            "date": "",
        },
    },
    "themarker.com": {
        "properties": {
            "http": {
                "referer": "",
                "user_agent": "",
            },
        },

        "selectors": {
            "headline": "header h1",
            "description": "header > p",
            "body": ".article-body-wrapper",
            "author": "",
            "date": "",
        },
    },
    "calcalist.co.il": {
        "selectors": {
            "headline": "h1 .title",
            "description": "h2.subTitle",
            "body": "#ArticleBodyComponent",
            "author": "",
            "date": "",
        },
    },
    "geektime.co.il": {
        "selectors": {
            "headline": "h1.head-title",
            "description": "p.head-sub-title",
            "body": "div#content",
            "author": "div.author",
            "date": "div.date",
        },
    },
    "nytimes.com": {
        "properties": {
            "http": {
                "referer": "",
                "user_agent": "",
            },
        },

        "selectors": {
            "headline": "h1",
            "description": "#article-summary",
            "body": "#live-feed-items > div",
            "author": ".last-byline",
            "date": "time",
        },
    },
    "economist.com": {
        "properties": {
            "http": {
                "referer": "",
                "user_agent": "",
            },
        },

        "selectors": {
            "headline": "h1",
            "description": "h2",
            "body": "section p",
            "author": "",
            "date": "time",
        },
    },
    "edition.cnn.com": {
        "properties": {
            "http": {
                "referer": "",
                "user_agent": "",
            },
        },

        "selectors": {
            "headline": "h1",
            "description": "",
            "body": ".article__content",
            "author": ".byline__name",
            "date": ".timestamp",
        },
    },
    "bbc.co.uk": {
        "properties": {
            "http": {
                "referer": "",
                "user_agent": "",
            },
        },

        "selectors": {
            "headline": "h1",
            "description": "",
            "body": "main article",
            "author": "",
            "date": "time",
        },
    },
}

def setup_logging(level):
    logging.basicConfig(level=level, format=LOG_FORMAT)
