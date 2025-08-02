import discord
from discord.ext import commands, tasks
import os
from datetime import datetime, timezone, timedelta
import asyncio

# 日本時間のタイムゾーン
JST = timezone(timedelta(hours=9))

# Botの設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} がログインしました！')
    print(f'Bot ID: {bot.user.id}')
    
    # スラッシュコマンドを同期
    try:
        synced = await bot.tree.sync()
        print(f'{len(synced)}個のスラッシュコマンドを同期しました')
    except Exception as e:
        print(f'スラッシュコマンドの同期に失敗しました: {e}')
    
    # 30日ごとの自動実行を開始
    auto_time_check.start()

@bot.tree.command(name='time', description='現在の時刻を表示します')
async def time_command(interaction: discord.Interaction):
    """現在時刻を返すスラッシュコマンド"""
    # 日本時間で現在時刻を取得
    now_jst = datetime.now(JST)
    
    # フォーマットされた時刻文字列を作成
    time_str = now_jst.strftime('%Y年%m月%d日 %H:%M:%S (JST)')
    
    # Embedメッセージを作成
    embed = discord.Embed(
        title="🕐 現在時刻",
        description=f"**{time_str}**",
        color=0x00ff00,
        timestamp=now_jst
    )
    embed.set_footer(text="自動TimeBot")
    
    await interaction.response.send_message(embed=embed)
    print(f'時刻コマンドが実行されました: {time_str}')

@tasks.loop(hours=24)
async def auto_time_check():
    """30日ごとに自動でtimeコマンドを実行"""
    # ループが開始されてから30日ごとに実行
    await asyncio.sleep(30 * 24 * 60 * 60)  # 30日待機
    
    # 最初のギルド（サーバー）のシステムチャンネルまたは最初のテキストチャンネルを取得
    guild = bot.guilds[0] if bot.guilds else None
    if guild:
        channel = guild.system_channel or discord.utils.get(guild.channels, type=discord.ChannelType.text)
        if channel:
            # 現在時刻を取得
            now_jst = datetime.now(JST)
            time_str = now_jst.strftime('%Y年%m月%d日 %H:%M:%S (JST)')
            
            # 自動メッセージを送信
            embed = discord.Embed(
                title="🤖 自動時刻チェック",
                description=f"**{time_str}**\n\n自動実行",
                color=0x0099ff,
                timestamp=now_jst
            )
            embed.set_footer(text="30日間隔での自動実行")
            
            try:
                await channel.send(embed=embed)
                print(f'自動時刻チェックが実行されました: {time_str}')
            except Exception as e:
                print(f'自動メッセージの送信に失敗しました: {e}')

@bot.event
async def on_command_error(ctx, error):
    """エラーハンドリング"""
    if isinstance(error, commands.CommandNotFound):
        return
    print(f'エラーが発生しました: {error}')

# Botを起動
if __name__ == '__main__':
    TOKEN = os.getenv('DISCORD_TOKEN')
    if TOKEN:
        bot.run(TOKEN)
    else:
        print('DISCORD_TOKENが設定されていません。環境変数を確認してください。')
