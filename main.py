import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import matplotlib.pyplot as plt
import io
import requests
from googletrans import Translator
import qrcode
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from keep_alive import keep_alive
from datetime import datetime, timedelta
import asyncio  # asyncioを追加

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True


class MyClient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents)
        self.timers = {}
        self.stopwatches = {}
        self.laps = {}
        self.pomodoros = {}

    async def setup_hook(self):
        await self.tree.sync()


client = MyClient()

translator = Translator()


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="現在開発中"))
    print(f"ログインしました: {client.user}")


# Help command
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
        name="/timer set <time> <label>",
        value="指定した時間のタイマーをセットします (例: /timer set 10m Study)",
        inline=False,
    )
    embed.add_field(
        name="/timer list",
        value="設定されているタイマーの一覧を表示します",
        inline=False,
    )
    embed.add_field(
        name="/stopwatch start <label>",
        value="指定した名前でストップウォッチを開始します (例: /stopwatch start Workout)",
        inline=False,
    )
    embed.add_field(
        name="/stopwatch lap <label>",
        value="ストップウォッチのラップタイムを記録します (例: /stopwatch lap Workout)",
        inline=False,
    )
    embed.add_field(
        name="/stopwatch stop <label>",
        value="ストップウォッチを停止して時間を表示します (例: /stopwatch stop Workout)",
        inline=False,
    )
    embed.add_field(
        name="/stopwatch reset <label>",
        value="ストップウォッチをリセットします (例: /stopwatch reset Workout)",
        inline=False,
    )
    embed.add_field(
        name="/pomodoro <label> <work_time> <short_break> <cycles> <long_break>",
        value="ポモドーロタイマーを設定します (例: /pomodoro Study 25 5 4 15)",
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
    await interaction.response.send_message(embed=embed)


# Math command
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


# Define command
@client.tree.command(name="define", description="単語の定義を表示します")
async def define(interaction: discord.Interaction, word: str):
    try:
        # 入力された単語の言語を検出
        detection = translator.detect(word)
        lang = detection.lang

        # 辞書APIの呼び出し
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


# Translate command
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
        print(f"Translating text: {text} to language: {language.value}")
        translation = translator.translate(text, dest=language.value)
        if translation is None:
            raise ValueError("翻訳に失敗しました。")

        print(f"Translation result: {translation.text}")

        embed = discord.Embed(
            title="翻訳結果",
            color=0x3498DB,
            description=f"**原文 ({translation.src})**: {text}\n**翻訳 ({language.name})**: {translation.text}",
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        print(f"Error in translate command: {e}")
        await interaction.response.send_message(f"Error: {e}")


# QR code command
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


# Decode QR code command
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


# Timer command
@client.tree.command(name="timer", description="タイマー機能")
@app_commands.describe(
    action="タイマーの操作 (set, list, cancel)",
    time="タイマーの時間 (例: 10m)",
    label="タイマーのラベル",
)
async def timer(
    interaction: discord.Interaction, action: str, time: str = None, label: str = None
):
    try:
        if action == "set":
            if not time or not label:
                raise ValueError("時間とラベルを指定してください。")

            time_units = {"s": "seconds", "m": "minutes", "h": "hours"}
            unit = time[-1]
            if unit not in time_units:
                raise ValueError(
                    "時間の単位は 's', 'm', 'h' のいずれかでなければなりません。"
                )

            seconds = int(
                timedelta(**{time_units[unit]: int(time[:-1])}).total_seconds()
            )
            end_time = datetime.now() + timedelta(seconds=seconds)
            client.timers[label] = end_time

            await interaction.response.send_message(
                f"タイマー '{label}' が {time} 後に終了します。"
            )
            await timer_end(interaction, label, seconds)

        elif action == "list":
            if not client.timers:
                await interaction.response.send_message(
                    "現在設定されているタイマーはありません。"
                )
            else:
                timers_list = "\n".join(
                    [
                        f"{label}: {end_time.strftime('%H:%M:%S')}"
                        for label, end_time in client.timers.items()
                    ]
                )
                await interaction.response.send_message(
                    f"設定されているタイマー:\n{timers_list}"
                )

        elif action == "cancel":
            if not label or label not in client.timers:
                raise ValueError("キャンセルするタイマーのラベルを指定してください。")

            del client.timers[label]
            await interaction.response.send_message(
                f"タイマー '{label}' がキャンセルされました。"
            )

        else:
            raise ValueError(
                "無効な操作です。set, list, cancelのいずれかを指定してください。"
            )

    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")


async def timer_end(interaction, label, seconds):
    await asyncio.sleep(seconds)
    if label in client.timers:
        del client.timers[label]
        await interaction.followup.send(f"タイマー '{label}' が終了しました！")


# Stopwatch command
@client.tree.command(name="stopwatch", description="ストップウォッチ機能")
@app_commands.describe(
    action="ストップウォッチの操作 (start, lap, stop, reset)",
    label="ストップウォッチのラベル",
)
async def stopwatch(interaction: discord.Interaction, action: str, label: str):
    try:
        if action == "start":
            if label in client.stopwatches:
                raise ValueError("既に動作中のストップウォッチがあります。")
            client.stopwatches[label] = datetime.now()
            client.laps[label] = []
            await interaction.response.send_message(
                f"ストップウォッチ '{label}' が開始されました。"
            )

        elif action == "lap":
            if label not in client.stopwatches:
                raise ValueError("動作中のストップウォッチが見つかりません。")
            lap_time = datetime.now() - client.stopwatches[label]
            client.laps[label].append(lap_time)
            await interaction.response.send_message(
                f"ストップウォッチ '{label}' のラップタイム: {lap_time}"
            )

        elif action == "stop":
            if label not in client.stopwatches:
                raise ValueError("動作中のストップウォッチが見つかりません。")
            elapsed_time = datetime.now() - client.stopwatches[label]
            del client.stopwatches[label]
            await interaction.response.send_message(
                f"ストップウォッチ '{label}' が停止しました。経過時間: {elapsed_time}"
            )

        elif action == "reset":
            if label in client.stopwatches:
                del client.stopwatches[label]
            if label in client.laps:
                del client.laps[label]
            await interaction.response.send_message(
                f"ストップウォッチ '{label}' がリセットされました。"
            )

        else:
            raise ValueError(
                "無効な操作です。start, lap, stop, resetのいずれかを指定してください。"
            )

    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")


# Pomodoro command
@client.tree.command(name="pomodoro", description="ポモドーロタイマー機能")
@app_commands.describe(
    label="ポモドーロタイマーのラベル",
    work_time="作業時間（分）",
    short_break="短い休憩時間（分）",
    cycles="ポモドーロの繰り返し回数",
    long_break="長い休憩時間（分）",
    action="ポモドーロタイマーの操作 (start, stop, reset)",
)
async def pomodoro(
    interaction: discord.Interaction,
    label: str,
    action: str,
    work_time: int = None,
    short_break: int = None,
    cycles: int = None,
    long_break: int = None,
):
    try:
        user_pomodoro = f"{interaction.user.id}-{label}"

        if action == "start":
            if user_pomodoro in client.pomodoros:
                raise ValueError("既にポモドーロタイマーが動作中です。")

            client.pomodoros[user_pomodoro] = {"continue": True, "count": 0}
            await interaction.response.send_message(
                f"ポモドーロタイマー '{label}' が開始されました。作業時間: {work_time}分、短い休憩: {short_break}分、繰り返し回数: {cycles}回、長い休憩: {long_break}分。"
            )

            while (
                client.pomodoros[user_pomodoro]["continue"]
                and client.pomodoros[user_pomodoro]["count"] < 10
            ):
                for cycle in range(cycles):
                    if not client.pomodoros[user_pomodoro]["continue"]:
                        break
                    await asyncio.sleep(work_time * 60)
                    await interaction.followup.send(
                        f"作業時間が終了しました。短い休憩を取ってください。({short_break}分) [{cycle + 1}/{cycles}]"
                    )
                    await asyncio.sleep(short_break * 60)
                    client.pomodoros[user_pomodoro]["count"] += 1

                if client.pomodoros[user_pomodoro]["count"] < 10:
                    await interaction.followup.send(
                        f"全てのポモドーロサイクルが完了しました。長い休憩を取ってください。({long_break}分)"
                    )
                    await asyncio.sleep(long_break * 60)
                else:
                    await interaction.followup.send(
                        f"10回のポモドーロサイクルが完了しました。続けますか？ (はい/いいえ) 1分以内に応答してください。"
                    )
                    try:
                        response = await client.wait_for(
                            "message",
                            check=lambda message: message.author == interaction.user
                            and message.channel == interaction.channel
                            and message.content in ["はい", "いいえ"],
                            timeout=60.0,
                        )
                        if response.content == "はい":
                            client.pomodoros[user_pomodoro]["count"] = 0
                        else:
                            client.pomodoros[user_pomodoro]["continue"] = False
                    except asyncio.TimeoutError:
                        client.pomodoros[user_pomodoro]["continue"] = False

            del client.pomodoros[user_pomodoro]
            await interaction.followup.send(
                f"ポモドーロタイマー '{label}' が終了しました。"
            )

        elif action == "stop":
            if user_pomodoro not in client.pomodoros:
                raise ValueError("動作中のポモドーロタイマーが見つかりません。")
            del client.pomodoros[user_pomodoro]
            await interaction.response.send_message(
                f"ポモドーロタイマー '{label}' が停止されました。"
            )

        elif action == "reset":
            if user_pomodoro in client.pomodoros:
                del client.pomodoros[user_pomodoro]
            await interaction.response.send_message(
                f"ポモドーロタイマー '{label}' がリセットされました。"
            )
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")


TOKEN = os.getenv("DISCORD_TOKEN")

keep_alive()

client.run(TOKEN)
