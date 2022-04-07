import asyncio
import json
import sys

from tools.db import D_language as lang


async def main(data, locate_file):
    for i in data.keys():
        tmp = await lang.find_one({'_id': i})
        tmp: dict
        if tmp is None:
            await lang.insert_one({'_id': i, 'name': data[i]})
        else:
            tmp[locate_file] = data[i]
            await lang.update_one({'_id': i}, {'$set': tmp})


if __init__ == "__main__":

    locate_file = input('>')

    try:
        with open('language' + locate_file + '.json', 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(e)
        sys.exit(-1)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(data, locate_file))
    loop.close()