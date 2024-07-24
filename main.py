import discord
import os
from discord.ext import commands
from discord import app_commands
from keep_alive import keep_alive
import matplotlib.pyplot as plt
import io
import requests
from googletrans import Translator
import qrcode
from forex_python.converter import CurrencyRates
from PIL import Image
import cv2
import numpy as np
from pyzbar.pyzbar import decode

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
currency_rates = CurrencyRates()


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
    embed.add_field(
        name="/qrcode <text>", value="テキストからQRコードを生成します", inline=False
    )
    embed.add_field(
        name="/decode_qrcode",
        value="アップロードされたQRコード画像を解読します",
        inline=False,
    )
    embed.add_field(
        name="/convert <amount> <from_currency> <to_currency>",
        value="指定した通貨を他の通貨に換算します (例: /convert 100 USD JPY)",
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
        # 入力された単語の言語を検出
        detection = translator.detect(word)
        lang = detection.lang

        response = requests.get(
            f"https://api.dictionaryapi.dev/api/v2/entries/{lang}/{word}"
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


@client.tree.command(name="qrcode", description="テキストからQRコードを生成します")
async def qrcode_command(interaction: discord.Interaction, text: str):
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        file = discord.File(buf, filename="qrcode.png")
        await interaction.response.send_message(file=file)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")


@client.tree.command(
    name="decode_qrcode", description="アップロードされたQRコード画像を解読します"
)
async def decode_qrcode(
    interaction: discord.Interaction, attachment: discord.Attachment
):
    try:
        img_data = await attachment.read()
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        decoded_objects = decode(img)
        if not decoded_objects:
            raise ValueError("QRコードが見つかりませんでした。")

        decoded_text = decoded_objects[0].data.decode("utf-8")
        embed = discord.Embed(
            title="QRコードの解読結果", color=0x3498DB, description=decoded_text
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")


@client.tree.command(name="convert", description="指定した通貨を他の通貨に換算します")
@app_commands.describe(
    amount="換算する金額", from_currency="元の通貨", to_currency="換算後の通貨"
)
async def convert(
    interaction: discord.Interaction,
    amount: float,
    from_currency: str,
    to_currency: str,
):
    try:
        converted_amount = currency_rates.convert(
            from_currency.upper(), to_currency.upper(), amount
        )
        embed = discord.Embed(
            title="通貨換算結果",
            color=0x1ABC9C,
            description=f"{amount} {from_currency.upper()} は {converted_amount:.2f} {to_currency.upper()} です。",
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")


TOKEN = os.getenv("DISCORD_TOKEN")

keep_alive()

client.run(TOKEN)
