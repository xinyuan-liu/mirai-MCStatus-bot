import mcstatus
import re
from mcstatus import MinecraftServer
from threading import Thread
from collections import deque
import time
from mctools import QUERYClient

server_ip = '192.168.1.3'

def get_server_list(annc):
    lines=annc.strip().split('\n') 
    splitter=(max(lines, key=lines.count))
    if lines.count(splitter) == 1:
        print('使用默认分割线：——')
        splitter='——'
    splitter+='\n'
    split=(annc.split(splitter))

    servers=[s.strip().split('\n') for s in split if not '服务器IP' in s]
    server_list=[]
    for server in servers:
        name_s=re.sub('【.*】','',server[0]).strip().split(' ')
        candidate=[]
        for s in name_s:
            if re.search('[0-9]+',s)!=None:
                candidate.append(s)
        if len(candidate)==0:
            print(server)
            version=''
            name=' '.join(name_s)
        else:
            version=candidate[-1]
            name=(' '.join(name_s[:name_s.index(version)]))
        for s in server[1:]:
            try:
                suffix, port=s.split('：')
            except Exception as e:
                print(s)
            if(suffix=='端口号'):
                server_list.append((name,port))
            else:
                server_list.append((name+' '+suffix,port))
    return server_list
    
def query_server(name, addr, retry=3):
    player_list=None
    version='offline'
    for i in range(retry):
        try:
            server = MinecraftServer.lookup(addr)
            status = server.status()
            sample = status.players.sample
            version = status.version.name
            if sample == None:
                player_list = []
            else:
                player_list = [player.name for player in sample]
            break
        except:
            pass
    # 有些情况下mcstatus有bug返回不了结果，在mcstatus连不上服务器的情况下尝试用MC的query功能查询服务器状态，需要在serer.properties里面打开query并且把query端口设成游戏端口一样的
    if version == 'offline':
        if True: # False
            try:
                ip, port=addr.split(':')
                port=int(port)
                query = QUERYClient(ip, port)
                query.set_timeout(3)
                s=query.get_full_stats()
                version = s['version']
                player_list= [player_name.replace('\x1b[0m', '') for player_name in s['players']]
            except:
                pass
    return (name, player_list, version)

def join_query_list(server, q):
    name=server[0]
    #for port in server[1]:
    port=server[1]
    addr=server_ip+':'+str(port)
    q.append(query_server(name,addr))

def query_all():
    with open('announcement.txt') as f:
        annc=f.read()
    servers=get_server_list(annc)
    threads=[]
    q=deque()
    for server in servers:
        threads.append(Thread(target=join_query_list, args=(server,q)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return(q)

def all_players():
    Q=query_all()
    return [q[:2] for q in Q]

def all_players_text():
    l=list(all_players())
    #print(l)
    s=[]
    for i in l:
        if i[1]!=None and len(i[1])!=0:
            s.append(f'【{i[0]}】\n'+'\n'.join(['- '+s for s in i[1]]))
    if len(s)==0:
        return '这个点没人玩游戏'
    s.sort()
    return '\n'.join(s)

def get_version_all():
    Q=query_all()
    s=[]
    for q in Q:
        s.append(f'【{q[0]}】 {q[2]}')
    s.sort()
    return '\n'.join(s)

def update_server(output,interval=60):
    running=True
    status=dict(all_players())
    while(running):
        time.sleep(interval)
        message=[]
        new_status=dict(all_players())
        for key in status:
            if key in new_status:
                sample = status[key]
                new_sample = new_status[key]
                if sample != None and new_sample != None:
                    sample=set(sample)
                    new_sample=set(new_sample)
                    num_players = len(new_sample)
                    if(num_players>10):
                        continue
                    join=new_sample.difference(sample)
                    leave=sample.difference(new_sample)
                    for p in join:
                        message.append(f'【{key}】{p}加入了游戏')
                    for p in leave:
                        message.append(f'【{key}】{p}离开了游戏')
                elif sample == None and new_sample == None:
                    continue
                elif sample == None and new_sample != None:
                    message.append(f'【{key}】服务器回来了')
                    for p in new_sample:
                        message.append(f'【{key}】{p}加入了游戏')
                elif sample != None and new_sample == None:
                    message.append(f'【{key}】服务器好像不见了')
                    for p in sample:
                        message.append(f'【{key}】{p}离开了游戏') 
        status=new_status
        if len(message)!=0:
            output('\n'.join(message))

if __name__=="__main__":
    update_server(output=print,interval=5)
