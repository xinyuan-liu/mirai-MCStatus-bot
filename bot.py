from graia.broadcast import Broadcast
from graia.application import GraiaMiraiApplication, Session
from graia.application.message.chain import MessageChain
import requests
import asyncio
from graia.application.message.elements.internal import Plain, At, App
from graia.application.friend import Friend
from graia.application.group import Group, Member
import server
from threading import Thread
from CustomEvents import ServerUpdateEvent
import base64
loop = asyncio.get_event_loop()

group_number = '111' #群号码

bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host="http://localhost:8080", # 填入 httpapi 服务运行的地址
        authKey="111", # 填入 authKey
        account=111, # 你的机器人的 qq 号
        websocket=True # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
    )
)

@bcc.receiver("GroupMessage")
async def group_message_handler(
    message: MessageChain,
    app: GraiaMiraiApplication,
    group: Group, member: Member,
):
    for i in message:
        if(type(i)==App):
            try:
                content = eval(i.dict()['content'])
                if type(content) == dict and content['app'] == 'com.tencent.mannounce':
                    announcement=(str(base64.b64decode(content['meta']['mannounce']['text'].encode('ascii')),'utf-8'))
            except Exception as e:
                print(e)
    if message.asDisplay().startswith("/say_hello"):
        await app.sendGroupMessage(group, MessageChain.create([
            At(member.id), Plain(" Hello world!")
        ]))
    elif message.asDisplay().startswith('/list'):
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(server.all_players_text())
        ]))
    elif message.asDisplay().startswith('/version'):
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(server.get_version_all())
        ]))
    elif message.asDisplay().startswith('/help'):
        await app.sendGroupMessage(group, MessageChain.create([
            Plain('/say_hello\n/list\n/version\n/help')
        ]))
    else:
        for i in message:
            if(type(i)==App):
                try:
                    content = eval(i.dict()['content'])
                    if type(content) == dict and content['app'] == 'com.tencent.mannounce':
                        announcement=(str(base64.b64decode(content['meta']['mannounce']['text'].encode('ascii')),'utf-8'))
                        if announcement.startswith('服务器IP：'):
                            with open('announcement.txt','w') as f:
                                f.write(announcement)
                            await app.sendGroupMessage(group, MessageChain.create([
                                Plain('公告更新成功！')
                            ]))
                except Exception as e:
                    print(e)

@bcc.receiver("ServerUpdateEvent")
async def server_update_message_handler(event: ServerUpdateEvent):
    message=event.message
    await app.sendGroupMessage(group_number, MessageChain.create([Plain(str(message))]))

def send_message(message):
    event = ServerUpdateEvent(message)
    bcc.postEvent(event)

t=Thread(target=server.update_server, args=(send_message,))
t.start()

app.launch_blocking()
