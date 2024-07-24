import discord
import os
from discord.ext import commands
from discord import app_commands
from keep_alive import keep_alive
import io
import qrcode
import requests
from googletrans import Translator
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
        name="/translate <text> <language>",
        value="テキストを指定した言語に翻訳します (例: /translate Hello Japanese)",
        inline=False,
    )
    embed.add_field(
        name="/qr_generate <text>",
        value="指定したテキストのQRコードを生成します",
        inline=False,
    )
    embed.add_field(
        name="/qr_decode",
        value="アップロードされた画像のQRコードを解読します",
        inline=False,
    )
    embed.add_field(
        name="/currency <amount> <from_currency> <to_currency>",
        value="指定した通貨を別の通貨に換算します (例: /currency 100 USD JPY)",
        inline=False,
    )
    await interaction.response.send_message(embed=embed)


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


@client.tree.command(
    name="qr_generate", description="指定したテキストのQRコードを生成します"
)
async def qr_generate(interaction: discord.Interaction, text: str):
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
    name="qr_decode", description="アップロードされた画像のQRコードを解読します"
)
async def qr_decode(interaction: discord.Interaction):
    try:
        if not interaction.attachments:
            await interaction.response.send_message(
                "画像がアップロードされていません。"
            )
            return

        attachment = interaction.attachments[0]
        img_data = await attachment.read()
        img = Image.open(io.BytesIO(img_data))
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        decoded_objects = decode(img)

        if not decoded_objects:
            await interaction.response.send_message("QRコードが見つかりませんでした。")
            return

        decoded_texts = [obj.data.decode("utf-8") for obj in decoded_objects]
        await interaction.response.send_message(
            f"解読されたQRコードの内容: {'; '.join(decoded_texts)}"
        )
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")


@client.tree.command(name="currency", description="指定した通貨を別の通貨に換算します")
async def currency(
    interaction: discord.Interaction,
    amount: float,
    from_currency: str,
    to_currency: str,
):
    try:
        c = CurrencyRates()
        result = c.convert(from_currency, to_currency, amount)
        await interaction.response.send_message(
            f"{amount} {from_currency} は {result:.2f} {to_currency} です"
        )
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")


TOKEN = os.getenv("DISCORD_TOKEN")

keep_alive()

client.run(TOKEN)
