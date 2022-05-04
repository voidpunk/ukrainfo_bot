import telebot, requests
from telegraph import Telegraph
from bs4 import BeautifulSoup
from func_timeout import func_timeout, FunctionTimedOut
import lxml.html.clean as clean
import re, time
from secrets import * # my tokens


this_bot = "BBC News\n"
bot = telebot.TeleBot(bot_token)
telegraph = Telegraph()
telegraph.create_account(short_name='9999')
safe_attrs = clean.defs.safe_attrs
cleaner = clean.Cleaner(safe_attrs_only=True, safe_attrs=frozenset())

url= "https://www.bbc.com/news/live/world-europe-60774819"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
article = {
    # "date": None,
    "title": None,
    "text": None
}
bot.send_message(personal_chat, f"{this_bot}Script restarted")

def post(images=None):
    if len(images) == 0:
        html = '{0}<br><a href="{1}">Source</a>'.format(
                                article['text'], url
                            )
    elif len(images) == 1:
        html = '<img src="{1}">{0}<br><a href="{2}">Source</a>'.format(
                                article['text'], images[0], url
                            )
    elif len(images) == 2:
        html = '<img src="{1}">{0}<img src="{3}"><br><a href="{2}">Source</a>'.format(
                                article['text'], images[0], url, images[1]
                            )
        print(html)
    else:
        bot.send_message(personal_chat, f"{this_bot}Too many images")

    telegraph_post = telegraph.create_page( 
                        title=article["title"],
                        author_name="@ukraine_info_en",
                        author_url="https://t.me/ukraine_info_en",
                        html_content=html
                    )
    return telegraph_post

check = 0
while True:
    try:
        if check == 120:
            bot.send_message(personal_chat, f"{this_bot}Bot online")
            check = 0

        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("article")
        last_article = articles[0]
        title = last_article.find("h3").text.strip().lower()
        
        if title == "our live coverage is moving" or title == "live page moving":
            url = last_article.find("a")["href"]
            continue

        html_raw = last_article.find("div", {"class": "lx-stream-post-body"})
        html_cleaned = cleaner.clean_html(str(html_raw))
        html = re.sub(r'<(/)?(div|noscript|body|html|span|svg|img)>', '', html_cleaned)
        src = last_article.find_all("img")
        images = []

        for img in src:
            img = img.get("data-src")
            if img:
                image =  img.replace("{width}", "624")
                images.append(image)

        if article["title"] != title or article["text"] != html:
            article = {
                # "date": date,
                "title": title,
                "text": html
            }
            if html == "":
                continue

            while True:
                try:
                    telegraph_post = func_timeout(5, post, args=(images,))
                    break
                except FunctionTimedOut:
                    # bot.send_message(personal_chat, f"{this_bot}Timeout")
                    pass
                except Exception as e:
                    bot.send_message(personal_chat, f"{this_bot}ERROR:\n\n{e}")

            bot.send_message(
                ukraine_info_en,
                parse_mode="markdown",
                text="\t*{}*\n\n[👇Read]({}) — [🇮🇹 @ucraina_info]({})".format(
                    article["title"],
                    telegraph_post['url'],
                    "https://t.me/ucraina_info",
                    disable_web_page_preview=True
                )
            )

    except Exception as e:
        bot.send_message(personal_chat, f"{this_bot}ERROR:\n\n{e}")
        continue

    time.sleep(30)
    check += 1
