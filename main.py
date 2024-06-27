import discord
import os
from discord.ext import commands
from supabase import create_client, Client
from keep_alive import keep_alive

# Supabaseクライアントを初期化
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True


class MyClient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()


client = MyClient()


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="Supabaseに接続中"))
    print(f"ログインしました: {client.user}")


@client.tree.command(name="setup", description="使い方の説明です")
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="現在の状況",
        color=0x00FF00,  # フレーム色指定(今回は緑)
        description="サイトからさらに詳しく見ることができます",
        url="https://example.com",  # これを設定すると、タイトルが指定URLへのリンクになる
    )
    embed.add_field(
        name="Get", value="現在の状況を取得することができます", inline=False
    )
    embed.add_field(
        name="Test", value="テスト機能を使用することができます", inline=False
    )
    embed.set_footer(
        text="現在時刻での状況です",  # フッターには開発者の情報でも入れてみる
    )
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="get", description="Supabaseからデータを取得します")
async def get(interaction: discord.Interaction):
    await interaction.response.defer()  # 一時的な応答を送信してインタラクションを保持する
    try:
        response = supabase.table("test").select("*").execute()
        data = response.data
        if not data:
            await interaction.followup.send("データがありません！")
        else:
            embed = discord.Embed(
                title="現在の状況",
                color=0x00FF00,  # フレーム色指定(今回は緑)
                description="サイトからさらに詳しく見ることができます",
                url="https://example.com",  # これを設定すると、タイトルが指定URLへのリンクになる
            )

            for row in data:
                embed.add_field(
                    name=row["name"],
                    value=f"{row['condition']}",
                    inline=False,
                )

            embed.set_footer(
                text="現在時刻での状況です",  # フッターには開発者の情報でも入れてみる
            )
            await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(
            f"データの取得中にエラーが発生しました: {str(e)}"
        )


@client.tree.command(name="test", description="テスト機能を表示します")
async def test(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Test機能",
        color=0xFF901E,  # フレーム色指定(今回は緑)
        description="未実装機能",
        url="https://example.com",  # これを設定すると、タイトルが指定URLへのリンクになる
    )
    await interaction.response.send_message(embed=embed)


TOKEN = os.getenv("DISCORD_TOKEN")

keep_alive()

client.run(TOKEN)
