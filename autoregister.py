'''
load a libary
'''
import asyncio
import json
import os
import sys

from tools.db import D_language as lang # load a language table


async def main(data, locate_file): # is main 
    for i in data.keys(): # i is short_t
        tmp = await lang.find_one({"_id": i}) # find short_t in language table
        tmp: dict # tmp is load a dict
        if tmp is None: # is None
            await lang.insert_one({"_id": i, locate_file: data[i]}) # insert new one
        else: # is in
            tmp[locate_file] = data[i] # short_t[locate_name] = locate[short_t_name]
            await lang.update_one({"_id": i}, {"$set": tmp}) # update a data


try:
    locate_file = sys.argv[1] # locate_file cli
except:
    locate_file = input(">") # type in if is None

try: # try
    with open( # open a language file with encode utf-8
        os.path.join(os.getcwd(), "language", locate_file + ".json"),
        "r+",
        encoding="UTF-8",
    ) as f:
        data = json.load(f) # data is language file content

except Exception as e: # is Error
    print(e) # Error type print
    sys.exit(-1) # exit

loop = asyncio.get_event_loop() # asyncio loop make
loop.run_until_complete(main(data, locate_file)) # run main in a loop
loop.close() # is done -> close
