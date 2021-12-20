import os.path
import discord
from discord import client
from selenium.webdriver.chrome import options
import yt_dlp
from yt_dlp import YoutubeDL
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from discord.utils import get
from discord import FFmpegPCMAudio
import asyncio
import time
from datetime import timezone, timedelta, datetime
timezone_kst=timezone(timedelta(hours=9))
import nacl
from discord.ext import commands
import sys

봇토큰="" #당신의 봇토큰을 넣어주세여
채널ID=000000000000000 #음악싸개가 있어야할 채널ID를 넣어주세요
명령어="!" #command_prefix
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
chromedriver_dir = "/app/.chromedriver/bin/chromedriver" #chromedriver dev

bot = commands.Bot(command_prefix = 명령어, help_command=None)
now_song=[] #지금 노래 정보 [제목,유튜브링크,재생용링크]
next_song=[] #다음 노래정보 [[노래1제목,링크],[노래2제목,링크]]
auto_song=0 #자동재생 on, off 기본 off
auto_song_playlist=[] #자동재생시 재생했던 노래들 url
auto_song_ban_title=["반복재생","반복 재생","1hour","1 hour","1시간","1 시간","연속듣기","(1hour)"] #자동재생시 제목에 있으면 안되는거
auto_song_playing = 0 #지금노래가 자동재생중으로 인한 노래인지 확인
auto_song_next=[] #빠른 자동재생을 위한 다음곡 미리받기
버전1=2.23
play_or_pause="⏯️" #리액션용
stop="⏹️" #스킵
shuffle="🔀" #자동재생
restart="❌" #재부팅
star="⭐" #즐겨찾기 추가

@bot.event
async def on_command_error(ctx, error): #에러시 채팅창에 표시
    try:
        if isinstance(error, commands.CommandNotFound): #존재하지 않는 명령어
            msg = await ctx.send("해당 명령어는 존재하지 않습니다!")
        if isinstance(error, commands.MissingRequiredArgument): #내용 없음
            msg = await ctx.send('내용을 입력해주세요!')
        print(error)
        await ctx.message.delete()
        print("에러발생!")
        time.sleep(5)
        await msg.delete()
    except:
        pass

@bot.event
async def on_ready():  #봇 켜지면 작동
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    global helpme
    global message
    global mid
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name=f"{명령어}help "))
    ch = bot.get_channel(채널ID)
    await ch.purge(limit=100) #채팅채널에 있는 내용 삭제
    embed=도움()
    helpme = await ch.send(embed=embed)
    embed = embed_play()
    message = await ch.send(embed =embed)
    await message.add_reaction(play_or_pause) #반응추가
    await message.add_reaction(stop)
    await message.add_reaction(shuffle)
    await message.add_reaction(restart)
    await message.add_reaction(star)
    mid = message
    await 새로고침(message,helpme)


@bot.event
async def on_message(message, pass_context=True): #메시지 오면 확인후 명령어 없으면 삭제
    if message.channel.id == 채널ID:
        if not message.content.startswith(명령어):
            if message.author.bot == 1:
                return
            await message.delete()
            return
        if message.content==명령어:
            await message.delete()
            return
        await bot.process_commands(message)


@bot.command()
async def 버전(ctx): #업데이트 기록중인데 대충함
    await ctx.message.delete()
    embed = discord.Embed(
        title="버전",
        colour=0x0097ff)

    embed.add_field(name="현재 버전",value=버전1,inline=False)  
    embed.add_field(name="2.0",value="리팩토링",inline=False)    
    embed.add_field(name="2.01",value="버그수정",inline=False) 
    embed.add_field(name="2.10",value="메시지 보기 편하게 바꿈",inline=False)     
    embed.add_field(name="2.15",value="리액션기능",inline=False)     
    embed.add_field(name="2.2",value="예외처리 될려나?",inline=False)
    embed.add_field(name="2.21",value="자동재생 타이틀 수정",inline=False)
    embed.add_field(name="2.22",value="유튜브 URL시 버그수정",inline=False)
    embed.add_field(name="2.23",value="youtube_dl에서 yt-dlp로 바꿈",inline=False)
    channel = await ctx.author.create_dm()
    await channel.send(embed=embed)

def 도움(): #도움말 내용

    embed = discord.Embed(
        title="도움말",
        colour=0x0097ff)

    embed.add_field(name=f"{명령어}exit",value="음악싸개가 방에서 퇴장합니다.겸 재부팅, 뭔가 고장나면 치셈",inline=False)
    embed.add_field(name=f"{명령어}p , {명령어}재생",value="노래 제목 또는 유튜브링크를 넣으면 틀어줍니다.",inline=False)
    embed.add_field(name=f"{명령어}s , {명령어}스킵",value="다음노래로 넘어갑니다",inline=False)
    embed.add_field(name=f"{명령어}dl(숫자) , {명령어}재생목록삭제(숫자)",value="해당 번호의 재생목록을 없애줍니다",inline=False)
    embed.add_field(name=f"{명령어}cl , 재생목록초기화",value="재생목록을 초기화합니다.",inline=False)
    embed.add_field(name=f"{명령어}자동재생 , 자동재생종료",value="다음노래 틀어줌(딜레이 10초 정도 있음)",inline=False)
    embed.add_field(name=f"{명령어}즐겨찾기, {명령어}B, {명령어}F (DM으로 감)",value=f"추가 = {명령어}즐겨찾기추가, {명령어}B+, {명령어}F+\n제거 = {명령어}즐겨찾기삭제(숫자) {명령어}B- {명령어}F- ",inline=False)
    return embed


@bot.event
async def on_reaction_add(reaction, user): #반응 클릭시 됨
    if user.bot == 1: #봇이면 패스
        return None
    if str(reaction.emoji) == play_or_pause: #멈추거나 실행
        if vc.is_paused():
            vc.resume()
            await reaction.remove(user)
            return
        if vc.is_playing():
            vc.pause()
            await reaction.remove(user)
            return
    if str(reaction.emoji) == stop: #노래 끔 다음노래재생
        if vc.is_playing():
            vc.stop()
            await reaction.remove(user)
        else:
            return
    if str(reaction.emoji) == shuffle: #자동재생
        global auto_song
        if auto_song == 0:
            auto_song = 1
            await reaction.remove(user)
            return
        if auto_song == 1:
            auto_song = 0
            await reaction.remove(user)
            return
    if str(reaction.emoji) == restart: #봇 재부팅
        sys.exit()
    if str(reaction.emoji) == star:
        userid = user.id
        file = f"./joy/{userid}.txt"
        if not os.path.isfile(file): #즐겨찾기없다면 userid로 파일만듬
            f = open(f"./joy/{userid}.txt","w")
            f.close()

        list_file = open(file, 'r').read().split('\n')
        list_file = list(filter(None,list_file))
        i=0
        f = open(f"./joy/{userid}.txt","a")
        if len(list_file)==0:
            f.write(f"[{now_song[0]}]({now_song[1]})")
        
        else:
            f.write(f"\n[{now_song[0]}]({now_song[1]})")
        f.close()

        channel = await user.create_dm()
        await channel.send(embed = discord.Embed(title= "즐겨찾기", description = f"[{now_song[0]}]({now_song[1]})이(가) 정상적으로 추가되었어요", color = 0x0097ff))
        await reaction.remove(user)

@bot.command(aliases=["h","도움","help"]) #입력시 DM으로 보냄
async def 도움말(ctx):
    await ctx.message.delete()
    embed=도움()
    channel = await ctx.author.create_dm()
    await channel.send(embed=embed)

async def 새로고침(message,helpme): #노래 상태 1초마다 변경
    while not bot.is_closed():
        try:
            embed=embed_play()
            await message.edit(embed=embed)
            embed=도움()
            await helpme.edit(embed=embed)
            await asyncio.sleep(1)
        except:
            try:
                play_next(lctx)
            except:
                sys.exit()

def tlwkr(ctx): #에러뜨길래 한번 해봄
    try:
        vc.play(discord.FFmpegPCMAudio(now_song[2], **FFMPEG_OPTIONS), after=lambda e:play_next(ctx))
    except:
        play_next(ctx)


def embed_play(): #노래 임베드 내용
    datetime_utc = datetime.utcnow()
    datetime_kst = datetime_utc.astimezone(timezone_kst)
    now1 = datetime_kst.strftime("%H:%M:%S")
    embed_playing = discord.Embed(
        title=f"상태    {now1}",
        colour=discord.Color.blue())
    if len(now_song)==0:
        embed_playing.add_field(name="노래",value="꺼져있음",inline=False)
        return embed_playing

    embed_playing.set_thumbnail(url=now_song[3])
    if auto_song == 1:
        embed_playing.add_field(name="노래          자동재생 ON",value=f"[{now_song[0]}]({now_song[1]})",inline=False)
    if auto_song == 0:
        embed_playing.add_field(name="노래          자동재생 OFF",value=f"[{now_song[0]}]({now_song[1]})",inline=False)
    if len(next_song) > 0:
        Text = ""
        for i in range(len(next_song)):
            Text = Text + "\n" + str(i + 1) + ". " + f"[{next_song[i][0]}]({next_song[i][1]})"
        embed_playing.add_field(name="재생목록",value=Text.strip(),inline=False)
    return embed_playing

def search(msg): #유튜브 검색
    if "https://www.youtube.com/" in msg: #유튜브 링크로 확인
        yturl = msg
        
        options = webdriver.ChromeOptions()
        options.binary_location = '/app/.apt/usr/bin/google-chrome'
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        driver = webdriver.Chrome("/app/.chromedriver/bin/chromedriver", options = options)
        driver.get(msg)
        source = driver.page_source
        bs = bs4.BeautifulSoup(source, 'lxml')
        title = bs.select_one("body > div > meta").get('content')
        thumbnailtest = bs.select("body > div > link")[1].get('href')
        print(title)
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(yturl, download=False)
            formats = info['formats']
        for fmt in formats:
            if fmt['format_id'] == '140':
                URL=fmt['url']
        driver.quit()
        return title, yturl, URL, thumbnailtest #제목 유튜브주소 음악재생용YDL링크 썸네일 링크
    주소 = "https://www.youtube.com/results?search_query="+msg #검색

    options = webdriver.ChromeOptions()
    options.binary_location = '/app/.apt/usr/bin/google-chrome'
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    driver = webdriver.Chrome("/app/.chromedriver/bin/chromedriver", options = options)
    driver.get(주소)
    source = driver.page_source
    bs = bs4.BeautifulSoup(source, 'lxml')
    entire = bs.find_all('a', {'id': 'video-title'}) #검색 결과 목록
    thumbnail = bs.select(' #dismissible > ytd-thumbnail > a > yt-img-shadow > img') #썸네일 목록
    entireNum = entire[0]
    thumbnailNum = thumbnail[0]
    title = entireNum.text.strip()
    test1 = entireNum.get('href')
    thumbnailtest = thumbnailNum.get('src')
    yturl = 'https://www.youtube.com'+test1 #영상의 주소

    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(yturl, download=False)
        formats = info['formats']
    for fmt in formats:
        if fmt['format_id'] == '140':
            URL=fmt['url']
    return title, yturl, URL, thumbnailtest #제목 유튜브주소 음악재생용YDL링크 썸네일 링크

def next_search(): #자동재생시 다음노래 검색

    options = webdriver.ChromeOptions()
    options.binary_location = '/app/.apt/usr/bin/google-chrome'
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    driver = webdriver.Chrome("/app/.chromedriver/bin/chromedriver", options = options)
    driver.get(now_song[1])
    time.sleep(3)
    source = driver.page_source
    bs = bs4.BeautifulSoup(source, 'lxml')
    next_song_thumbnail = bs.select('#dismissible > ytd-thumbnail > a > yt-img-shadow > img')
    next_song_yturl = bs.select('#dismissible > div > div.metadata.style-scope.ytd-compact-video-renderer > a')
    next_song_title = bs.select('#dismissible > div > div.metadata.style-scope.ytd-compact-video-renderer > a > h3 > span')
    thumbnailNum = next_song_thumbnail[0]
    thumbnailtest = thumbnailNum.get('src')
    i=0
    num=0
    while i !=1: #자동재생시 같은노래 반복금지
        titlelist=next_song_title[num]
        title=titlelist["title"]
        hreflist= next_song_yturl[num]
        href=hreflist["href"]
        num = num+1
        if href not in auto_song_playlist:
            i2=0
            while i2<len(auto_song_ban_title)-1:
                if auto_song_ban_title[i2] not in title:
                    i2+=1
                    if i2==len(auto_song_ban_title)-1:
                        i+=1
                if auto_song_ban_title[i2] in title:
                    i2+=100
    auto_song_playlist.append(href)
    driver.quit()
    yturl = 'https://www.youtube.com'+href
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(yturl, download=False)
        formats = info['formats']
    for fmt in formats:
        if fmt['format_id'] == '140':
            URL=fmt['url']

    return title, yturl, URL, thumbnailtest

def play_next(ctx): #노래 종료후 다음
    global auto_song_playing
    global auto_song
    try:
        mc = len(bot.voice_clients[0].channel.voice_states) #멤버 수 확인후 없으면 나감
        if mc<=1:
            now_song.clear()
            next_song.clear()
            auto_song=0
            auto_song_playlist.clear()
            auto_song_playing = 0 
            auto_song_next.clear()
            bot.loop.create_task(vc.disconnect())
            return
    except:
        now_song.clear()
        next_song.clear()
        auto_song=0
        auto_song_playlist.clear()
        auto_song_playing = 0 
        auto_song_next.clear()
    
    if len(next_song) >= 1: #다음노래 있으면 그거 재생
        if not vc.is_playing():
            auto_song_playlist.clear()
            now_song.clear()
            now_song.extend(next_song[0])
            del next_song[0]
            auto_song_playing=0
            tlwkr(ctx)
            return
    elif len(next_song)==0 and len(auto_song_next)>=1 and auto_song_playing==1 and auto_song==1: #자동재생시 대기열 추가
        if not vc.is_playing():
            now_song.clear()
            now_song.extend(auto_song_next)
            auto_song_playing=1
            tlwkr(ctx)
            title, yturl, URL, thumbnailtest=next_search()
            a=[title, yturl, URL, thumbnailtest]
            auto_song_next.clear()
            auto_song_next.extend(a)
            return

    elif len(next_song)==0 and auto_song==1 : #자동재생
        if not vc.is_playing():
            title, yturl, URL, thumbnailtest=next_search()
            a=[title, yturl, URL, thumbnailtest]
            now_song.clear()
            now_song.extend(a)
            auto_song_playing=1
            tlwkr(ctx)
            title, yturl, URL, thumbnailtest=next_search()
            a=[title, yturl, URL, thumbnailtest]
            auto_song_next.clear()
            auto_song_next.extend(a)
            return

    else:
        if not vc.is_playing(): #없으면 나가고 재부팅
            now_song.clear()
            bot.loop.create_task(vc.disconnect())
            
            sys.exit()

@bot.command(aliases=["p","ㅔ","재생"]) #음악 재생 명령어
async def play(ctx, *, msg):
    global vchannel
    global auto_song_playing
    global vc
    global lctx
    lctx = ctx
    auto_song_playlist.clear()
    auto_song_next.clear()
    auto_song_playing=0
    vchannel=ctx.author.voice.channel

    if bot.voice_clients == []:
        await vchannel.connect()
    
    vc = get(bot.voice_clients, guild=ctx.guild) #여기서부터
    await ctx.message.delete()
    if msg=="호랑수월가":
        msg="https://www.youtube.com/watch?v=ki_s8lVwkX0"
        title, yturl, URL, thumbnailtest = search(msg)
        if len(now_song)==0:
            a = [title,yturl, URL, thumbnailtest]
            now_song.extend(a)
            tlwkr(ctx)
        else:
            a = [title,yturl, URL, thumbnailtest]
            next_song.append(a)
        return #여기까지 삭제해도됨

    title, yturl, URL, thumbnailtest = search(msg)
    
    if len(now_song)==0: #지금 노래에 아무것도 없으면 재생
        a = [title,yturl, URL, thumbnailtest]
        now_song.extend(a)
        tlwkr(ctx)
        
    else: #있으면 next_song에 넣기
        a = [title,yturl, URL, thumbnailtest]
        next_song.append(a)

@bot.command(aliases=["s","스킵","ㄴ"]) #노래 종료 또는 스킵
async def 노래끄기(ctx):
    await ctx.message.delete()
    if vc.is_playing():
        vc.stop()
    else:
        return

@bot.command(aliases=["재부팅","reboot","re"]) #봇 재부팅
async def exit(ctx):
    await ctx.message.delete()
    vc = get(bot.voice_clients, guild=ctx.guild)
    await vc.disconnect(force=True)
    sys.exit()

@bot.command(aliases=["재생목록삭제","deletelist","dl"]) #재생대기열에 있는거 삭제
async def 목록삭제(ctx, *, number):
    await ctx.message.delete()
    try:
        del next_song[int(number)-1]
    except:
        if len(next_song) == 0:
            msg = await ctx.send("대기열에 노래가 없어 삭제할 수 없어요!")
            time.sleep(5)
            await msg.delete()
        elif len(next_song) < int(number):
            msg = await ctx.send("숫자의 범위가 목록개수를 벗어났습니다!")
            time.sleep(5)
            await msg.delete()
        elif number=="":
            msg = await ctx.send("숫자를 입력해주세요!")
            time.sleep(5)
            await msg.delete()

@bot.command(aliases=["재생목록초기화","listclaer","lc","cl"]) #재생대기열 초기화
async def 목록초기화(ctx):
    await ctx.message.delete()
    auto_song_playlist.clear()
    try:
        next_song.clear()
    except:
        msg=await ctx.send("아직 아무노래도 등록하지 않았어요.")
        time.sleep(5)
        await msg.delete()

@bot.command() #자동재생 시작
async def 자동재생(ctx):
    await ctx.message.delete()
    global auto_song
    if auto_song == 1:
        auto_song = 0
    auto_song = 1

@bot.command() #자동재생 종료
async def 자동재생종료(ctx):
    await ctx.message.delete()
    global auto_song
    auto_song = 0

@bot.command(aliases=["f","F","b","B","bookmark","ㄹ","ㅠ"]) #즐겨찾기 확인 DM으로 옴
async def 즐겨찾기(ctx):
    await ctx.message.delete()
    userid = ctx.message.author.id
    file = f"./joy/{userid}.txt"
    if not os.path.isfile(file): #즐겨찾기없다면 userid로 파일만듬
        f = open(f"./joy/{userid}.txt","w")
        f.close()
    
    list_file = open(file, 'r').read().split('\n')
    list_file = list(filter(None,list_file))
    i=0
    if len(list_file)==0:
        channel = await ctx.author.create_dm()
        await channel.send(embed = discord.Embed(title= "즐겨찾기", description = "아직 아무노래도 등록되지 않았어요.", color = 0x0097ff))
    else:
        global Text
        Text = ""
        while i < len(list_file):
            Text = Text + "\n" + str(i+1) + ". " + str(list_file[i])
            i+=1
        channel = await ctx.author.create_dm()
        await channel.send(embed = discord.Embed(title= "즐겨찾기", description = Text.strip(), color = 0x0097ff))

@bot.command(aliases=["f+","F+","b+","B+","ㄹ+","ㅠ+"]) #즐겨찾기 추가
async def 즐겨찾기추가(ctx, *, msg):
    await ctx.message.delete()
    userid = ctx.message.author.id
    music, ytrul, URL, thumbnailtest = search(msg)

    file = f"./joy/{userid}.txt"
    if not os.path.isfile(file): #즐겨찾기없다면 userid로 파일만듬
        f = open(f"./joy/{userid}.txt","w")
        f.close()

    list_file = open(file, 'r').read().split('\n')
    list_file = list(filter(None,list_file))
    i=0
    f = open(f"./joy/{userid}.txt","a")
    if len(list_file)==0:
        f.write(f"[{music}]({ytrul})")
    
    else:
        f.write(f"\n[{music}]({ytrul})")
    f.close()

    channel = await ctx.author.create_dm()
    await channel.send(embed = discord.Embed(title= "즐겨찾기", description = f"[{music}]({ytrul})이(가) 정상적으로 추가되었어요", color = 0x0097ff))

@bot.command(aliases=["f-","F-","b-","B-","ㄹ-","ㅠ-"]) #즐겨찾기 삭제
async def 즐겨찾기삭제(ctx, *, number):
    await ctx.message.delete()
    userid = ctx.message.author.id
    file = f"./joy/{userid}.txt"
    if not os.path.isfile(file): #즐겨찾기없다면 userid로 파일만듬
        f = open(f"./joy/{userid}.txt","w")
        f.close()
    
    list_file = open(file, 'r').read().split('\n')
    list_file = list(filter(None,list_file))
    if len(list_file) < int(number):
        msg = await ctx.send("입력한 숫자가 잘못되었거나 즐겨찾기의 범위를 초과하였습니다.")
        time.sleep(5)
        await msg.delete()
    elif len(list_file) >= int(number):
        f=open(f"./joy/{userid}.txt","w")
        number1=int(number)-1
        del list_file[number1]
        f.write('\n'.join(list_file))
        channel = await ctx.author.create_dm()
        await channel.send(embed = discord.Embed(title= "즐겨찾기", description = f"{number}번째 즐겨찾기가 삭제되었어요.", color = 0x0097ff))



bot.run(봇토큰)