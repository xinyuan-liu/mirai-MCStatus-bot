from graia.broadcast import Broadcast
from graia.application import GraiaMiraiApplication, Session
from graia.application.message.chain import MessageChain
import requests
import asyncio
from graia.application.message.elements.internal import Plain, At
from graia.application.friend import Friend
from graia.application.group import Group, Member
import server
from threading import Thread
from CustomEvents import ServerUpdateEvent
loop = asyncio.get_event_loop()

bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host="http://localhost:8080", # 填入 httpapi 服务运行的地址
        authKey="1042378432778", # 填入 authKey
        account=536779323, # 你的机器人的 qq 号
        websocket=True # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
    )
)

@bcc.receiver("GroupMessage")
async def group_message_handler(
    message: MessageChain,
    app: GraiaMiraiApplication,
    group: Group, member: Member,
):
    if message.asDisplay().startswith("/say_hello"):
        #print(app.connect_info.sessionKey)
        #gc=await app.getGroupConfig(group)
        #print(gc)
        #r=requests.get(app.connect_info.host+'/groupConfig',params={'sessionKey':app.connect_info.sessionKey, 'target':group.id})
        #print(r.text)
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

@bcc.receiver("ServerUpdateEvent")
async def server_update_message_handler(event: ServerUpdateEvent):
    message=event.message
    await app.sendGroupMessage('868348211', MessageChain.create([Plain(str(message))]))

def send_message(message):
    event = ServerUpdateEvent(message)
    bcc.postEvent(event)
    #try:
    #    await app.sendGroupMessage('868348211', MessageChain.create([Plain(str(message))]))
    #except:
    #    pass
#send_message('test')
t=Thread(target=server.update_server, args=(send_message,))
t.start()

app.launch_blocking()
