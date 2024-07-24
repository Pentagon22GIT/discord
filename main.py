import discord
import os
from discord.ext import commands
from discord import app_commands
from keep_alive import keep_alive
import matplotlib.pyplot as plt
import io
import requests
from googletrans import Translator

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True


class MyClient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()


client = MyClient()

translator = Translator()


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="現在開発中"))
    print(f"ログインしました: {client.user}")


@client.tree.command(name="help", description="コマンドの一覧と説明を表示します")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="ヘルプ", color=0x3498DB, description="以下は利用可能なコマンドの一覧です"
    )
    embed.add_field(
        name="/math <formula>", value="数式を画像として表示します", inline=False
    )
    embed.add_field(name="/define <word>", value="単語の定義を表示します", inline=False)
    embed.add_field(
        name="/translate <text> <language>",
        value="テキストを指定した言語に翻訳します (例: /translate Hello Japanese)",
        inline=False,
    )
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="math", description="数式を画像として表示します")
async def math(interaction: discord.Interaction, formula: str):
    try:
        if not formula:
            raise ValueError("数式が空です。")

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


@client.tree.command(name="define", description="単語の定義を表示します")
async def define(interaction: discord.Interaction, word: str):
    try:
        response = requests.get(
            f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        )
        data = response.json()

        if response.status_code != 200 or not data:
            raise ValueError("単語の定義が見つかりませんでした。")

        definition = data[0]["meanings"][0]["definitions"][0]["definition"]
        embed = discord.Embed(
            title=f"{word}の定義", color=0xE74C3C, description=definition
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")


@client.tree.command(name="translate", description="テキストを指定した言語に翻訳します")
@app_commands.describe(text="翻訳するテキスト", language="翻訳先の言語")
@app_commands.choices(
    language=[
        app_commands.Choice(name="Japanese", value="ja"),
        app_commands.Choice(name="English", value="en"),
        app_commands.Choice(name="Spanish", value="es"),
        app_commands.Choice(name="French", value="fr"),
        app_commands.Choice(name="German", value="de"),
        app_commands.Choice(name="Chinese", value="zh-cn"),
        app_commands.Choice(name="Korean", value="ko"),
        app_commands.Choice(name="Russian", value="ru"),
        app_commands.Choice(name="Italian", value="it"),
        app_commands.Choice(name="Portuguese", value="pt"),
    ]
)
async def translate(
    interaction: discord.Interaction, text: str, language: app_commands.Choice[str]
):
    try:
        translation = translator.translate(text, dest=language.value)
        embed = discord.Embed(
            title="翻訳結果",
            color=0x3498DB,
            description=f"**原文 ({translation.src})**: {text}\n**翻訳 ({language.name})**: {translation.text}",
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")


TOKEN = os.getenv("DISCORD_TOKEN")

keep_alive()

client.run(TOKEN)
