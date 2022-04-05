'''
Database Load tool
example) from tools.db import YOURDB
'''
import motor.motor_asyncio as motor

dbclient = motor.AsyncIOMotorClient("localhost", 27017)

db = dbclient.tjdb

D_users = db.users

D_language = db.language

D_customprefix = db.ctprefix
D_blacklists = db.blacklists
D_coinposts = db.coins

D_u_cb = db.user_chatbot
D_guilds = db.guilds