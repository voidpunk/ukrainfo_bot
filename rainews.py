import telebot, requests
from telegraph import Telegraph
from googlesearch import search
from bs4 import BeautifulSoup
from func_timeout import func_timeout, FunctionTimedOut
import datetime, time
from secrets import * # my tokens

this_bot = "RAI News\n"
bot = telebot.TeleBot(bot_token)
telegraph = Telegraph()
telegraph.create_account(short_name='9999')

war_day = 20
url= "https://www.rainews.it/maratona/2022/03/live-guerra-in-ucraina-la-cronaca-minuto-per-minuto-giorno-20-a67029a3-cf0b-44f6-940b-2bfe70c0a7cf.html"
article = {
    # "date": None,
    "title": None,
    "text": None
}
bot.send_message(personal_chat, f"{this_bot}Script restarted")

def post():
    telegraph_post = telegraph.create_page(
                        title=article["title"],
                        author_name="@ucraina_info",
                        author_url="https://t.me/ucraina_info",
                        html_content="{}<br><a href=\"{}\">Fonte</a>".format(
                            article['text'], url
                        )
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
        war_day = int(soup.find("h1").text[-2:])
        today = int(datetime.date.today().strftime("%d"))
        if today+36 != war_day:
            war_day = today+36
            query = f"Live guerra in Ucraina, la cronaca minuto per minuto giorno {war_day}"
            result = search(query, tld="it", num=1, stop=1, pause=2)
            url = next(result)
            bot.send_message(personal_chat, f"{this_bot}Changing url to:\n{url}")

        articles = soup.find_all("div", {"class": "article__content__unit article__content__unit--text fullsmall"})
        last_article = articles[0]
        # date = last_article.find("div", {"class": "grid-x info-share-wrapper"}).text.strip().replace(" ", " - ", 1)
        title = last_article.find("div", {"class": "cell-title"}).text.strip()
        text = last_article.find("div", {"class": "cell-description"}).text.strip()

        if article["title"] != title or article["text"] != text:
            article = {
                # "date": date,
                "title": title,
                "text": text
            }

            while True:
                try:
                    telegraph_post = func_timeout(5, post)
                    break
                except FunctionTimedOut:
                    # bot.send_message(personal_chat, f"{this_bot}Timeout")
                    pass
                except Exception as e:
                    bot.send_message(personal_chat, f"{this_bot}ERROR:\n\n{e}")

            bot.send_message(
                ucraina_info,
                parse_mode="markdown", 
                text="\t*{}*\n\n[👇Leggi]({}) — [🇬🇧 @ukraine_info_en]({})".format(
                    article["title"],
                    telegraph_post['url'],
                    "https://t.me/ukraine_info_en"
                )
            )

    except Exception as e:
        bot.send_message(personal_chat, f"{this_bot}ERROR:\n\n{e}")
        continue

    time.sleep(30)
    check += 1
