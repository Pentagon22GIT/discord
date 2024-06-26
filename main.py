import discord
import os
from supabase import create_client, Client
from keep_alive import keep_alive

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)


class MyClient(discord.Client):
    async def on_ready(self):
        print(f"ログインしました: {self.user}")

    async def on_message(self, message):
        print(f"送信: {message.author}: {message.content}")

        # Bot自身のメッセージは無視する
        if message.author == self.user:
            return

        # メッセージの内容を比較する
        if message.content == "Hello":
            await message.channel.send("Hello!")
            print("move1")

        elif message.content == "Get":
            print("move2")
            await self.get_data(message)

    async def get_data(self, message):
        print("move3")
        try:
            response = supabase.table("test").select("*").execute()

            data = response.data
            if not data:
                await message.channel.send("データがありません！")
            else:
                data_str = "\n".join(
                    f"{row['date']} - {row['name']} - {row['number_of_people']}"
                    for row in data
                )
                await message.channel.send(f"取得したデータ:\n{data_str}")

        except Exception as e:
            await message.channel.send(
                f"データの取得中にエラーが発生しました: {str(e)}"
            )


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)

TOKEN = os.getenv("DISCORD_TOKEN")

keep_alive()

client.run(TOKEN)
