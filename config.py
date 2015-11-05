#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
本文件用于存放各类配置相关的东西
"""

import os
from flask import (Flask)
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache
from peewee import *
from playhouse.flask_utils import FlaskDB, get_object_or_404, object_list
from playhouse.sqlite_ext import *

# 路径变量
APP_DIR = os.path.dirname(os.path.realpath(__file__))

# 数据库路径
DATABASE = 'sqliteext:///%s' % os.path.join(APP_DIR, 'data/blog.db')
DEBUG = False

# 定义用户密码
ADMIN_NAME = 'admin'
ADMIN_PASSWORD = 'admin'


# 定义名称,ip端口等
SITE_NAME = '小博客'
HOST = '127.0.0.1:5000'

# 控制cookie 的私有密钥
SECRET_KEY = '1111'

# 媒体对象控制相关,用于 markdown 转html
SITE_WIDTH = 800
oembed_providers = bootstrap_basic(OEmbedCache())

# 初始化,以及数据库相关
app = Flask(__name__)
app.config.from_object(__name__)
flask_db = FlaskDB(app)
database = flask_db.database