import discord
import os
from discord.ext import commands
from keep_alive import keep_alive
import matplotlib.pyplot as plt
import io

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
        name="Test", value="テスト機能を使用することができます", inline=False
    )
    embed.set_footer(
        text="現在時刻での状況です",  # フッターには開発者の情報でも入れてみる
    )
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="test", description="テスト機能を表示します")
async def test(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Test機能",
        color=0xFF901E,  # フレーム色指定(今回は緑)
        description="未実装機能",
        url="https://example.com",  # これを設定すると、タイトルが指定URLへのリンクになる
    )
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="math", description="数式を画像として表示します")
async def math(interaction: discord.Interaction, formula: str):
    try:
        # 数式を画像に描画
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, f"${formula}$", fontsize=30, ha="center", va="center")
        ax.axis("off")

        # 画像をバイナリデータに変換
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close(fig)

        # 画像をDiscordに送信
        file = discord.File(buf, filename="formula.png")
        await interaction.response.send_message(file=file)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")


TOKEN = os.getenv("DISCORD_TOKEN")

keep_alive()

client.run(TOKEN)
