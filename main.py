import discord
import os
from supabase import create_client, Client

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)


class MyClient(discord.Client):
    async def on_ready(self):
        await client.change_presence(
            activity=discord.Game(name="Connecting with supabase")
        )
        print(f"ログインしました: {self.user}")

    async def on_message(self, message):
        print(f"送信: {message.author}: {message.content}")

        # Bot自身のメッセージは無視する
        if message.author == self.user:
            return

        # メッセージの内容を比較する
        if message.content == "help":
            embed = discord.Embed(
                title="現在の状況",
                color=0x00FF00,  # フレーム色指定(今回は緑)
                description="サイトからさらに詳しく見ることができます",
                url="https://example.com",  # これを設定すると、タイトルが指定URLへのリンクになる
            )

            # embed.set_author(
            #    name=client.user,  # Botのユーザー名
            #    url="https://repo.exapmle.com/bot",  # titleのurlのようにnameをリンクにできる。botのWebサイトとかGithubとか
            # )

            # embed.set_thumbnail(
            #   url="https://image.example.com/thumbnail.png"
            # )  # サムネイルとして小さい画像を設定できる

            # embed.set_image(
            #    url="https://image.example.com/main.png"
            # )  # 大きな画像タイルを設定できる

            embed.add_field(
                name="Get", value="現在の状況を取得することができます", inline=False
            )
            embed.add_field(
                name="Test",
                value="テスト機能を使用することができます",
                inline=False,
            )

            embed.set_footer(
                text="現在時刻での状況です",  # フッターには開発者の情報でも入れてみる
                # icon_url="https://dev.exapmple.com/profile.png",
            )
            await message.channel.send(embed=embed)

        elif message.content == "Get":
            await self.get_data(message)

        elif message.content == "Test":
            embed = discord.Embed(
                title="Test機能",
                color=0xFF901E,  # フレーム色指定(今回は緑)
                description="未実装機能",
                url="https://example.com",  # これを設定すると、タイトルが指定URLへのリンクになる
            )

            await message.channel.send(embed=embed)

    async def get_data(self, message):
        try:
            response = supabase.table("test").select("*").execute()

            data = response.data
            if not data:
                await message.channel.send("データがありません！")
            else:
                embed = discord.Embed(
                    title="現在の状況",
                    color=0x00FF00,  # フレーム色指定(今回は緑)
                    description="サイトからさらに詳しく見ることができます",
                    url="https://example.com",  # これを設定すると、タイトルが指定URLへのリンクになる
                )

                for row in data:
                    embed.add_field(
                        name=row["date"],
                        value=f"{row['name']} - {row['number_of_people']}",
                        inline=False,
                    )

                embed.set_footer(
                    text="現在時刻での状況です",  # フッターには開発者の情報でも入れてみる
                    # icon_url="https://dev.exapmple.com/profile.png",
                )

                await message.channel.send(embed=embed)

        except Exception as e:
            await message.channel.send(
                f"データの取得中にエラーが発生しました: {str(e)}"
            )


intents = discord.Intents.default()
intents.message_content = True
intents.presences = True

client = MyClient(intents=intents)

TOKEN = os.getenv("DISCORD_TOKEN")

client.run(TOKEN)
