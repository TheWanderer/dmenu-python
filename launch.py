#!/usr/bin/python
import pickle
import commands
import sys
import os
import subprocess
from operator import itemgetter

CACHE_FILE = os.getenv('HOME')+'/.launch'
DMENU = "dmenu"
TERM = "urxvt -e "
CD_TERM = "urxvt -e zsh -c 'cd "
FOLDERS = ["/home/shankar"]
EXT = {
        '.txt':'urxvt -e vim',
        '.sh':'urxvt -e vim',
        '.py':'urxvt -e vim'
        }
FILEBROWSER = "pcmanfm"


def create_cache():
    prog_list = commands.getoutput("dmenu_path").split("\n")
    dirlist = []

    for watchdir in FOLDERS:
         for root, dir , files in os.walk(watchdir):
             if root.find('/.')  == -1 : 
                 for name in files:
                     if not name.startswith('.'):
                         if os.path.splitext(name)[1] in EXT.keys(): 
                             dirlist.append(os.path.join(root,name))
                 for name in dir: 
                     if not name.startswith('.'):
                         dirlist.append(os.path.join(root,name))

    dirlist.append("update_dmen")
    dirlist.sort()
    
    return dict.fromkeys(prog_list + dirlist,0)
    

def store(object,file):
    with open(file, 'w') as f:
        pickle.dump(object,f)
    f.close()

def create_new(file):
    cache = create_cache()
    store(cache,file)
    return cache

def retrieve(file,ifnotfound):
    try:
        with open(file,'r+') as f:
            obj = pickle.load(f)
        f.close()
        return(obj)
    except:
        return ifnotfound(file)

def update():
    cache_new  = create_cache()
    cache_old  = retrieve(CACHE_FILE,create_new)
    for k in cache_old:
        if k in cache_new:
            cache_new[k] = cache_old[k]

    store(cache_new,CACHE_FILE)

def dmenu(pgm_list):
    p = subprocess.Popen([DMENU,"-l","10"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out = p.communicate("\n".join(pgm_list))[0]
    return out


def run():
    cache = retrieve(CACHE_FILE,create_new)
    sorted_list = sorted(cache.iteritems(), key=itemgetter(1), reverse=True)
    pgm_list = [ x[0] for x in sorted_list ]
    out = dmenu(pgm_list)
    if len(out) > 0 :
        if out == "update_dmen":
            update()
        elif out.endswith(';'):
            out = out[:-1]
            if os.path.isdir(out):
                os.system(CD_TERM + out + " && zsh '")
            else:
                os.system(TERM + out + " &")
        elif out.find('/') != -1:
            if os.path.isdir(out):
                os.system(FILEBROWSER + " " + out + " &")
            else:
                (main,ext) = os.path.splitext(out)
                if ext == '':
                    os.system(out + " &")
                else:
                    os.system(EXT[ext] + " " + out + " &")
        else:
            os.system(out + " &")

        if not cache.has_key(out):
            cache[out] = 0
        cache[out] += 1
        store(cache,CACHE_FILE)

run()

