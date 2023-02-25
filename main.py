import os
import random

import iluxaMod as ilm

database = ilm.postgreSQL_connect(user="postgres", password="armageddon", database="tgsenderbot", host="illyashost.ddns.net")
database.init_DB(stages=True, staff=True, stdout=False)
db = database.db
sql = database.sql

def preDB():
    sql.execute(f"CREATE TABLE IF NOT EXISTS names(row_id TEXT PRIMARY KEY, firstname TEXT, lang TEXT)")
    db.commit()
    sql.execute(f"CREATE TABLE IF NOT EXISTS texts(row_id TEXT PRIMARY KEY, caption TEXT, lang TEXT)")
    db.commit()

preDB()
tgbot = ilm.tgBot(open("TOKEN", "r").read())
bot = tgbot.bot
btn = tgbot.btn
back = tgbot.back
kmarkup = tgbot.kmarkup
send = tgbot.send
bot.parse_mode = "HTML"


@bot.message_handler(commands=["start"])
def start_message(message):
    chat_id = message.chat.id
    if message.chat.type == "private":
        if database.staff(chat_id) == "admin":
            sql.execute(f"SELECT * FROM texts WHERE lang != 'None'")

            send(chat_id, f"You have to send {str(len(sql.fetchall()))} reviews")
            k = kmarkup()
            msg = "Select an action"
            k.row(btn("Start", callback_data="start"))
            k.row(btn("Add variation", callback_data="variations"))
            send(chat_id, msg, reply_markup=k)
            database.stages(chat_id, "None")


@bot.message_handler(content_types=['text'])
def globalText(message):
    chat_id = message.chat.id
    stage = database.stages(chat_id).split("||")
    if message.chat.type == "private":
        if stage[0] == "variations":
            k = kmarkup()
            msg = "Send new review content"
            k.row(back("home"))
            send(chat_id, msg, reply_markup=k)
            database.stages(chat_id, f"var_review||{message.text}")
        elif stage[0] == "var_review":
            k = kmarkup()
            msg = "Send lang of review"

            name = stage[1]
            review = message.text
            review_lang = "None"

            row_id = random.randint(1, 99999999)

            sql.execute(f"SELECT * FROM names WHERE lang = '{str(review_lang)}' AND firstname = '{str(name)}'")
            if sql.fetchone() is None:

                sql.execute(
                    f"INSERT INTO names VALUES ('{str(row_id)}', '{str(name)}', '{str(review_lang)}')")
                db.commit()

                sql.execute(
                    f"INSERT INTO texts VALUES('{str(row_id)}', '{str(review)}', '{str(review_lang)}')")
                db.commit()

            b1 = btn("ru", callback_data=f"review_lang||{str(row_id)}||ru")
            b2 = btn("en", callback_data=f"review_lang||{str(row_id)}||en")
            b3 = btn("he", callback_data=f"review_lang||{str(row_id)}||he")
            k.row(b1, b2, b3)
            k.row(back("home"))
            send(chat_id, msg, reply_markup=k)
            database.stages(chat_id, f"None")



@bot.callback_query_handler(func=lambda m: True)
def globalCalls(call):
    chat_id = call.message.chat.id

    def dm():
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass

    if call.data == "variations":
        k = kmarkup()
        msg = "Enter Account Name"
        k.row(back("home"))
        send(chat_id, msg, reply_markup=k)
        dm()
        database.stages(chat_id, "variations")
    elif call.data == "home":
        start_message(call.message)
        dm()
    elif call.data == "start":
        os.system(f"python3 sendAd.py")
        send(chat_id, f"Review sended")
        sql.execute(f"SELECT * FROM texts WHERE lang != 'None'")

        send(chat_id, f"You have to send {str(len(sql.fetchall()))} reviews")
        start_message(call.message)
    elif call.data.split("||")[0] == "review_lang":
        row_id = call.data.split("||")[1]
        lang = call.data.split("||")[2]
        sql.execute(f"UPDATE names SET lang = '{str(lang)}' WHERE row_id = '{str(row_id)}'")
        db.commit()

        sql.execute(f"UPDATE texts SET lang = '{str(lang)}' WHERE row_id = '{str(row_id)}'")
        db.commit()
        send(chat_id, "Review added")

        k = kmarkup()
        msg = "Enter Account Name"
        k.row(back("home"))
        send(chat_id, msg, reply_markup=k)
        database.stages(chat_id, "variations")

while True:
    bot.polling()
