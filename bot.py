import discord , asyncio , datetime , sys , os
from parser import *
from chat import *
import pandas as pd

def main():
    client = discord.Client()
    
    
    #명령어 목록
    Command_list = (
                    "```css\n"
                    "[KJ_bot Command List]\n"
                    "!도움말 - 도움말\n"
                    "!버전 - 버전 정보\n"
                    "!현재시간 - 현재 시각\n"
                    "!오늘급식 - 오늘 급식\n"
                    "!내일급식 -  급식\n"
                    "!급식알려줘 - 급식 식단\n"
                    "!질문 - 무엇이든 물어보세요\n"
                    "```"
                    )
    #급식안내
    meal_notice = (
                    "```css\n"
                    "[-] '1월'과 '1일'이 제대로 입력되지 않는 문제 발생(수정 예정)\n"
                    "[-] 2022년 1월 2일 인 경우 22102 로 보낼 것.\n"
                    "[-] 2022년 7월 1일 인 경우 22071 로 보낼 것.\n"
                    "```"
                    )
    #대화시스템 안내
    chat_notice = (
                    "```css\n"
                    "[무엇이든 물어보세요.]\n"
                    "ex. 컴퓨터실 어디야\n"
                    "ex. 1학년 교무실 어디야\n"
                    "ex. **선생님 성함이 "
                    "```"
                    )
   
   
    @client.event
    async def on_member_join(member):
        fmt = ' {1.name} 에 오신걸 환영합니다, {0.mention} 님'
        channel = member.guild.get_channel(1000968326874411041)
        await channel.send(fmt.format(member, member.guild))
        await channel.send("공지 읽어주세요")

    @client.event
    async def on_member_remove(member):
        channel = member.guild.get_channel(1000968326874411041)
        fmt = '{0.mention} 님이 서버에서 나가셨습니다.'
        await channel.send(fmt.format(member, member.guild))

    @client.event
    async def on_ready():
        print('봇이 준비되었습니다')
        print(client.user.name)
        print(client.user.id)
        print('---------')
        await client.change_presence(status=discord.Status.online, activity=None)

    @client.event
    async def print_get_meal(local_date, local_weekday, message):
        l_diet = get_diet(2, local_date, local_weekday)
        d_diet = get_diet(3, local_date, local_weekday)

        if len(l_diet) == 1:
            embed = discord.Embed(title="No Meal", description="급식이 없습니다.", color=0x00ff00)
            await message.channel.send(message.channel, embed=embed)
        elif len(d_diet) == 1:
            lunch = local_date + " 중식\n" + l_diet
            embed = discord.Embed(title="Lunch", description=lunch, color=0x00ff00)
            await message.channel.send(message.channel, embed=embed)
        else:
            lunch = local_date + " 중식\n" + l_diet
            dinner = local_date + " 석식\n" + d_diet
            embed= discord.Embed(title="Lunch", description=lunch, color=0x00ff00)
            await message.channel.send(message.channel, embed=embed)
            embed = discord.Embed(title="Dinner", description=dinner, color=0x00ff00)
            await message.channel.send(message.channel, embed=embed)
           
    bad = ['ㅅㅂ','시발','야발','씨발','씨@발','시1발','씨1발','시@발','씨@발','썅','개새끼','개새기','새끼','좆까','ㅈ까','씹','병신','ㅄ','ㅂ@ㅅ','씨발련','썅련','ㄴㄱㅁ','느금','느금마','엿먹어']

    @client.event
    async def on_message(message):
        message_contant=message.content
        for i in bad:
            if i in message_contant:
                await message.channel.send('욕설감지 ')
                await message.delete()

       
        if message.content.startswith('!도움말'):
            await message.channel.send(Command_list)

        elif message.content.startswith('!버전'):
            embed = discord.Embed(title="Bot Version", description="updated", color=0x00ff00)
            embed.add_field(name="Version", value="0.3.0", inline=False)
            await message.channel.send('일부 오류 수정 ')
            await message.channel.send(message.channel, embed=embed)

        elif message.content.startswith('!현재시간'):
            dt = datetime.datetime.now()
            local_time = dt.strftime("%Y년 %m월 %d일 %H시 %M분 %S초") + datetime.timedelta(hours=9)
            embed = discord.Embed(title="Local Time", description=local_time, color=0x00ff00)
            await message.channel.send(message.channel, embed=embed)

        elif message.content.startswith('!오늘급식'):
            f_dt = datetime.datetime.today() 
            meal_date = f_dt.strftime("%Y.%m.%d")
            whatday = f_dt.weekday()

            await print_get_meal(meal_date, whatday, message)
            
        elif message.content.startswith('!내일급식'):
            f_dt = datetime.datetime.today() 
            meal_date = f_dt.strftime("%Y.%m.%d") + datetime.timedelta(days=9)
            whatday = f_dt.weekday()

            await print_get_meal(meal_date, whatday, message)

        elif message.content.startswith('!급식알려줘'):
            request = meal_notice + '\n' + '날짜를 보내주세요...'
            request_e = discord.Embed(title="Send to Me", description=request, color=0xcceeff)
            await message.channel.send(message.channel, embed=request_e)
            def pred(m):
                return m.author == message.author
            try:
                meal_date = await client.wait_for('message', check=pred, timeout=15.0)
            except asyncio.TimeoutError:
                await message.channel.send('15초 내로 입력해주세요.')
            else:
                await message.channel.send('입력한 날짜는 {0.content}'.format(meal_date))

            meal_date = str(meal_date.content) # 221121
            meal_date = '20' + meal_date[:2] + '.' + meal_date[2:4] + '.' + meal_date[4:6] # 2022.11.21

            s = meal_date.replace('.', ', ') # 2022, 11, 21

            #한자리수 달인 경우를 해결하기위함
            if int(s[6:8]) < 10:
                s = s.replace(s[6:8], s[7:8])

            ss = "datetime.datetime(" + s + ").weekday()"
            try:
                whatday = eval(ss)
            except:
                warnning = discord.Embed(title="Plz Retry", description='올바른 값으로 다시 시도하세요 : !급식알려줘', color=0xff0000)
                await message.channel.send(message.channel, embed=warnning)
                return

            await print_get_meal(meal_date, whatday, message)
        
        elif message.content.startswith('!질문'):
            request = chat_notice + '\n' + '질문을 입력하세요...'
            request_e = discord.Embed(title="Send to Me", description=request, color=0xcceeff)
            await message.channel.send(message.channel, embed=request_e)
            def pred(m):
                return m.author == message.author
            try:
                question = await client.wait_for('message', check=pred, timeout=15.0)
                question = str(question.content)
            except asyncio.TimeoutError:
                await message.channel.send('15초 내로 입력해주세요.')
            else:
                await message.channel.send(chat(question))
            


    async def my_background_task():
        await client.wait_until_ready()
        channel = client.get_channel(1000968326874411041)
        while client.is_ready:
            await channel.send(Command_list)
            await asyncio.sleep(60*60*24)

    client.loop.create_task(my_background_task())
    client.run('MTAwMDk1NzU1MTM4ODY1OTg1Mg.GsOJMq.EXZHEM6kxxHPEouwD1wkUkzKBXRcwy_nZZSlsY')

    #대기 시간 초과로 봇이 종료되었을 때 자동으로 재실행을 위함
    #import sys, os
    executable = sys.executable
    args = sys.argv[:]
    args.insert(0, sys.executable)
    print("Respawning")
    os.execvp(executable, args)

if __name__ == '__main__':
    main()
  
