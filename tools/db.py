"""
Database Load tool
example) from tools.db import YOURDB
"""
from tools.config import config # load config

import motor.motor_asyncio as motor # load asyncio mongodb

dbclient = motor.AsyncIOMotorClient( # mongodb client
    config["database"]["address"], config["database"]["port"] # is use a config database address and port
)

db = dbclient.tjdb # database - tjdb

D_users = db.users # database - tjdb - users(table) is userdata

D_language = db.language # database - tjdb - language(table) is multi-language-text

D_customprefix = db.ctprefix # database - tjdb - ctprefix(table)  is custom prefix

D_blacklists = db.blacklists # database - tjdb - blacklists(table) is bot blacklist

D_coinposts = db.coins # database - tjdb - coins(table) is use a economy function

D_commands = db.cmds # database - tjdb - cmds(table) is record a command used count

D_achi = db.achievements # database - tjdb - achievements(table) is record a bot achievement, used achievements function

D_u_cb = db.user_chatbot # database - tjdb - user_chatbot(table) is used user's chatbot(custom)

D_guilds = db.guilds # database - tjdb - guilds(table) is record a guilds with use a bot
