#!/usr/bin/python
import pickle
import commands
import sys
import os
import subprocess
from operator import itemgetter

CACHE_FILE = os.getenv('HOME')+'/.launch'

def create_cache():
    prog_list = commands.getoutput("dmenu_path").split("\n")
    return dict.fromkeys(prog_list,0)

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
#    cache_new.update(cache_old)
    for k in cache_old:
        if k in cache_new:
            cache_new[k] = cache_old[k]

    store(cache_new,CACHE_FILE)

def run():
    cache = retrieve(CACHE_FILE,create_new)
    sorted_list = sorted(cache.iteritems(), key=itemgetter(1), reverse=True)
    pgm_list = [ x[0] for x in sorted_list ]
    p = subprocess.Popen(["dmenu"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out = p.communicate("\n".join(pgm_list))[0]
    if len(out) > 0 :
        print out 
        print cache[out]
        cache[out] += 1
        os.system(out + "&")
        store(cache,CACHE_FILE)

if sys.argv[1] == "update":
    update()
elif sys.argv[1] == "run":
    run()

