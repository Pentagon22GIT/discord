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
        self.timers_tasks = {}
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
        value="テキストを指定した言語に翻訳します。例: /translate Hello Japanese",
        inline=False,
    )
    embed.add_field(
        name="/timer <action> <time> <label>",
        value="タイマーを設定。例: /timer set 10m Study",
        inline=False,
    )
    embed.add_field(
        name="/stopwatch start <label>",
        value="ストップウォッチを設定。例: /stopwatch start Workout",
        inline=False,
    )
    embed.add_field(
        name="/pomodoro <label> <work_time> <short_break> <cycles> <long_break> <action>",
        value="ポモドーロタイマーを設定します。例: /pomodoro Study 25 5 4 15",
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
            duration = int(time[:-1])
            timer_time = timedelta(**{time_units[unit]: duration})

            end_time = datetime.now() + timer_time
            client.timers[label] = end_time

            embed = discord.Embed(
                title="タイマーセット",
                color=0x2ECC71,
                description=f"ラベル: {label}\n時間: {time}\n終了予定時刻: {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
            )
            await interaction.response.send_message(embed=embed)

            if label in client.timers_tasks:
                client.timers_tasks[label].cancel()

            client.timers_tasks[label] = asyncio.create_task(
                timer_task(interaction, label, timer_time)
            )
        elif action == "list":
            if not client.timers:
                await interaction.response.send_message(
                    "現在設定されているタイマーはありません。"
                )
                return

            embed = discord.Embed(title="タイマーリスト", color=0x3498DB)
            for label, end_time in client.timers.items():
                remaining_time = end_time - datetime.now()
                embed.add_field(
                    name=label,
                    value=f"残り時間: {remaining_time}\n終了予定時刻: {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
                    inline=False,
                )
            await interaction.response.send_message(embed=embed)
        elif action == "cancel":
            if not label:
                raise ValueError("キャンセルするタイマーのラベルを指定してください。")

            if label not in client.timers:
                raise ValueError("指定されたラベルのタイマーが見つかりません。")

            del client.timers[label]

            if label in client.timers_tasks:
                client.timers_tasks[label].cancel()
                del client.timers_tasks[label]

            embed = discord.Embed(
                title="タイマーキャンセル",
                color=0xE74C3C,
                description=f"ラベル: {label} のタイマーがキャンセルされました。",
            )
            await interaction.response.send_message(embed=embed)
        else:
            raise ValueError(
                "無効な操作です。action は 'set', 'list', 'cancel' のいずれかです。"
            )
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")


async def timer_task(interaction, label, duration):
    await asyncio.sleep(duration.total_seconds())
    embed = discord.Embed(
        title="タイマー終了",
        color=0xE74C3C,
        description=f"ラベル: {label} のタイマーが終了しました。",
    )
    await interaction.followup.send(embed=embed)


# Stopwatch command
@client.tree.command(name="stopwatch", description="ストップウォッチ機能")
@app_commands.describe(
    action="ストップウォッチの操作 (start, stop, lap, reset)",
    label="ストップウォッチのラベル",
)
async def stopwatch(interaction: discord.Interaction, action: str, label: str):
    try:
        if action == "start":
            if label in client.stopwatches:
                raise ValueError("既に同じラベルのストップウォッチが存在します。")

            client.stopwatches[label] = datetime.now()
            client.laps[label] = []

            embed = discord.Embed(
                title="ストップウォッチスタート",
                color=0x2ECC71,
                description=f"ラベル: {label} のストップウォッチが開始されました。",
            )
            await interaction.response.send_message(embed=embed)
        elif action == "stop":
            if label not in client.stopwatches:
                raise ValueError("指定されたラベルのストップウォッチが見つかりません。")

            start_time = client.stopwatches.pop(label)
            elapsed_time = datetime.now() - start_time
            laps = client.laps.pop(label, [])

            embed = discord.Embed(
                title="ストップウォッチストップ",
                color=0xE74C3C,
                description=f"ラベル: {label} のストップウォッチが停止されました。\n経過時間: {elapsed_time}\nラップ: {laps}",
            )
            await interaction.response.send_message(embed=embed)
        elif action == "lap":
            if label not in client.stopwatches:
                raise ValueError("指定されたラベルのストップウォッチが見つかりません。")

            lap_time = datetime.now() - client.stopwatches[label]
            client.laps[label].append(lap_time)

            embed = discord.Embed(
                title="ラップ記録",
                color=0x3498DB,
                description=f"ラベル: {label}\nラップ時間: {lap_time}",
            )
            await interaction.response.send_message(embed=embed)
        elif action == "reset":
            if label not in client.stopwatches:
                raise ValueError("指定されたラベルのストップウォッチが見つかりません。")

            client.stopwatches.pop(label)
            client.laps.pop(label, [])

            embed = discord.Embed(
                title="ストップウォッチリセット",
                color=0xE74C3C,
                description=f"ラベル: {label} のストップウォッチがリセットされました。",
            )
            await interaction.response.send_message(embed=embed)
        else:
            raise ValueError(
                "無効な操作です。action は 'start', 'stop', 'lap', 'reset' のいずれかです。"
            )
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")


# Pomodoro command
@client.tree.command(name="pomodoro", description="ポモドーロタイマー機能")
@app_commands.describe(
    label="ポモドーロのラベル",
    work_time="作業時間 (分)",
    short_break="短い休憩時間 (分)",
    cycles="サイクル数",
    long_break="長い休憩時間 (分)",
    action="操作 (start, stop)",
)
async def pomodoro(
    interaction: discord.Interaction,
    label: str,
    work_time: int,
    short_break: int,
    cycles: int,
    long_break: int,
    action: str,
):
    try:
        if action == "start":
            if label in client.pomodoros:
                raise ValueError("既に同じラベルのポモドーロが存在します。")

            embed = discord.Embed(
                title="ポモドーロスタート",
                color=0x2ECC71,
                description=f"ラベル: {label} のポモドーロが開始されました。\n作業時間: {work_time} 分\n短い休憩時間: {short_break} 分\nサイクル数: {cycles}\n長い休憩時間: {long_break} 分",
            )
            await interaction.response.send_message(embed=embed)

            client.pomodoros[label] = asyncio.create_task(
                pomodoro_task(
                    interaction, label, work_time, short_break, cycles, long_break
                )
            )
        elif action == "stop":
            if label not in client.pomodoros:
                raise ValueError("指定されたラベルのポモドーロが見つかりません。")

            client.pomodoros[label].cancel()
            del client.pomodoros[label]

            embed = discord.Embed(
                title="ポモドーロストップ",
                color=0xE74C3C,
                description=f"ラベル: {label} のポモドーロが停止されました。",
            )
            await interaction.response.send_message(embed=embed)
        else:
            raise ValueError("無効な操作です。action は 'start' または 'stop' です。")
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")


async def pomodoro_task(interaction, label, work_time, short_break, cycles, long_break):
    for cycle in range(1, cycles + 1):
        await asyncio.sleep(work_time * 60)
        embed = discord.Embed(
            title="ポモドーロ通知",
            color=0x3498DB,
            description=f"ラベル: {label}\n作業サイクル {cycle}/{cycles} が終了しました。短い休憩時間です。",
        )
        await interaction.followup.send(embed=embed)

        if cycle < cycles:
            await asyncio.sleep(short_break * 60)
        else:
            await asyncio.sleep(long_break * 60)

    embed = discord.Embed(
        title="ポモドーロ完了",
        color=0x2ECC71,
        description=f"ラベル: {label} の全てのサイクルが完了しました。",
    )
    await interaction.followup.send(embed=embed)


keep_alive()
client.run(os.getenv("DISCORD_TOKEN"))
