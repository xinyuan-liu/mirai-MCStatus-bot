import mcstatus
import re
from mcstatus import MinecraftServer
from threading import Thread
from collections import deque
import time

def get_server_list(annc, return_version=False):
    #print(annc)
    lines=annc.strip().split('\n')
    splitter=(max(lines, key=lines.count))+'\n'
    split=(annc.split(splitter))
    servers=[s.strip().split('\n') for s in split if not '服务器IP' in s]
    #print(servers)
    s_list=[]
    v_list=[]
    for server in servers:
        name_s=server[0].split(' ')
        candidate=[]
        for s in name_s:
            #print(s)
            if re.search('[0-9]+',s)!=None:
                #print(s)
                candidate.append(s)
        version=candidate[-1]
        v_list.append(version)
        #print(version)
        name=(' '.join(name_s[:name_s.index(version)]))
        ports=[]
        for s in server[1:]:
            ports.append(s.split('：')[1])
        s_list.append((name,ports))
    if not return_version:
        return s_list
    else:
        return s_list,v_list
    
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
    return (name, player_list, version)

def join_query_list(server, q):
    name=server[0]
    addr='192.168.1.59'+':'+str(server[1][0])
    q.append(query_server(name,addr))

def all_querys():
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
    Q=all_querys()
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
    return '\n'.join(s)

def get_version_all():
    Q=all_querys()
    #dic=dict([(q[0],q[2]) for q in Q])
    #with open('announcement.txt') as f:
    #    annc=f.read()
    #s_list,v_list = get_server_list(annc,True)
    #for i in len(s_list):
    #    name=s_list[i]
    #    version=v_list[i]
    s=[]
    for q in Q:
        s.append(f'【{q[0]}】 {q[2]}')
    return '\n'.join(s)

def update_server(output,interval=60):
    #output=print
    running=True
    status=dict(all_players())
    #pending_leave={}
    while(running):
        time.sleep(interval)
        new_status=dict(all_players())
        for key in status:
            if key in new_status:
                sample = status[key]
                new_sample = new_status[key]
                if sample != None and new_sample != None:
                    sample=set(sample)
                    new_sample=set(new_sample)
                    join=new_sample.difference(sample)
                    leave=sample.difference(new_sample)
                    for p in join:
                        output(f'【{key}】{p}加入了游戏')
                    for p in leave:
                        #TODO pending_leave
                        output(f'【{key}】{p}离开了游戏')
                elif sample == None and new_sample == None:
                    continue
                elif sample == None and new_sample != None:
                    output(f'【{key}】服务器回来了')
                    for p in new_sample:
                        output(f'【{key}】{p}加入了游戏')
                elif sample != None and new_sample == None:
                    output(f'【{key}】服务器好像不见了')
                
        status=new_status
        #print(status)

if __name__=="__main__":
    #print(all_players_text())
    update_server(output=print,interval=5)
