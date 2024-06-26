import discord
import os
from keep_alive import keep_alive
from supabase import create_client

client = discord.Client(intents=discord.Intents.default())
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

@client.event
async def on_ready():
    print("ログインしました")

@client.event
async def on_message(message):
    if message.author.bot:  # ボット自身のメッセージには反応しない
        return
    
    if message.content.startswith("!data"):
        print("!dataコマンドがトリガーされました")
        data = get_data_from_supabase()
        if not data:
            await message.channel.send("データを取得できませんでした。")
        else:
            response = ""
            for row in data:
                response += f"日付: {row['date']}, 名前: {row['name']}, 人数: {row['number_of_people']}\n"
            await message.channel.send(response)
    else:
        # !data 以外のコマンドには反応しないようにする
        pass

def get_data_from_supabase():
    query = "SELECT * FROM test"
    response = supabase.query(query)
    if response.error:
        print(f"Supabase エラー: {response.error}")
        return None
    else:
        return response.data

TOKEN = os.getenv("DISCORD_TOKEN")
keep_alive()
client.run(TOKEN)
