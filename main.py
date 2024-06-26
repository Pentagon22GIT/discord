import discord
import os
import asyncio
from supabase import create_client
from keep_alive import keep_alive

# Initialize Supabase client
supabase_url = "SUPABASE_URL"
supabase_key = "SUPABASE_KEY"
supabase = create_client(supabase_url, supabase_key)


class MyClient(discord.Client):
    async def on_ready(self):
        print(f"ログインしました: {self.user}")

    async def on_message(self, message):
        print(f"送信: {message.author}: {message.content}")
        if message.author == self.user:
            return

        if message.content == "Hello":
            await message.channel.send("Hello!")

        if message.content == "Get":
            await self.get_data(message)

    async def get_data(self, message):
        try:
            # Query Supabase table 'test' for date, name, number_of_people
            query = supabase.from_("test").select("date, name, number_of_people")
            response = await query.execute()

            if response.error or not response.data:
                await message.channel.send("データがありません！")
            else:
                data_str = "\n".join(
                    f"{row['date']} - {row['name']} - {row['number_of_people']}"
                    for row in response.data
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
