import discord
import os
from discord.ext import commands
from keep_alive import keep_alive
import matplotlib.pyplot as plt
import io
import numpy as np

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True


class MyClient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()


client = MyClient()

math_history = {}


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
    embed.add_field(
        name="/history", value="過去に入力した数式を表示します", inline=False
    )
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="math", description="数式を画像として表示します")
async def math(interaction: discord.Interaction, formula: str):
    user_id = interaction.user.id
    if user_id not in math_history:
        math_history[user_id] = []
    math_history[user_id].append(formula)

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


@client.tree.command(name="history", description="過去に入力した数式を表示します")
async def history(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in math_history or not math_history[user_id]:
        await interaction.response.send_message("数式の履歴がありません。")
    else:
        history_str = "\n".join(math_history[user_id])
        await interaction.response.send_message(f"数式の履歴:\n{history_str}")


TOKEN = os.getenv("DISCORD_TOKEN")

keep_alive()

client.run(TOKEN)
