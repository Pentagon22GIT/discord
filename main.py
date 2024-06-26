import discord
import os
from keep_alive import keep_alive
from supabase import create_client, Client

# SupabaseのURLとAPIキー
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

client = discord.Client(intents=discord.Intents.default())


def get_data():
    try:
        response = supabase.table("your_table_name").select("*").execute()
        print(response.data)  # 取得したデータをログに出力
        return response.data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []


@client.event
async def on_ready():
    print("ログインしました")


@client.event
async def on_message(message):
    if message.content.startswith("!data"):
        print(
            "!dataコマンドがトリガーされました"
        )  # コマンドがトリガーされたことをログに出力
        data = get_data()
        if not data:
            await message.channel.send("データを取得できませんでした。")
        else:
            response = ""
            for row in data:
                response += f"日付け: {row['date']}, 名前: {row['name']}, 人数: {row['number_of_people']}\n"
            await message.channel.send(response)


TOKEN = os.getenv("DISCORD_TOKEN")
# Web サーバの立ち上げ
keep_alive()
client.run(TOKEN)
