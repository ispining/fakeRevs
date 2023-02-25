import iluxaMod as ilm
from pyrogram import Client
import random

database = ilm.postgreSQL_connect(user="postgres", password="armageddon", database="tgsenderbot", host="illyashost.ddns.net")
db = database.db
sql = database.sql

api_id = 23157084
api_hash = "dc5f3e26a82d15d87bb7d59c43ccdbf4"

def preDB():
    sql.execute(f"CREATE TABLE IF NOT EXISTS names(row_id TEXT PRIMARY KEY, firstname TEXT, lang TEXT)")
    db.commit()
    sql.execute(f"CREATE TABLE IF NOT EXISTS texts(row_id TEXT PRIMARY KEY, caption TEXT, lang TEXT)")
    db.commit()

preDB()

def generate_client_name(auto_delete=True):
    sql.execute(f"SELECT * FROM names WHERE lang != 'None'")
    generated_value = random.choice(sql.fetchall())
    row_id = generated_value[0]
    name = generated_value[1]

    if auto_delete:
        sql.execute(f"DELETE FROM names WHERE row_id = '{str(row_id)}'")
        db.commit()

    return name, generated_value[2]

def generate_caption(lang="he", auto_delete=True):
    sql.execute(f"SELECT * FROM texts WHERE lang = '{str(lang)}'")
    generated_value = random.choice(sql.fetchall())
    row_id = generated_value[0]
    caption = generated_value[1]

    if auto_delete:
        sql.execute(f"DELETE FROM texts WHERE row_id = '{str(row_id)}'")
        db.commit()

    return caption

with Client(name="ads_account", api_id=api_id, api_hash=api_hash) as app:
    data = generate_client_name()
    profile = {"name": data[0], "lang": data[1]}
    caption = generate_caption(profile['lang'])

    app.update_profile(first_name=profile['name'])
    app.send_message("@accountone1", caption)

with Client(name="accountOne", api_id=api_id, api_hash=api_hash) as app:

    def get_last_id():
        num = 0
        for dialog in app.get_chat_history("@esperanto111"):
                if dialog.id > num:
                    num = dialog.id
        return num

    app.forward_messages(chat_id="@ashrai_b", from_chat_id=5273614891, message_ids=[get_last_id()], disable_notification=True)

