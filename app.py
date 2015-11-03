#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime,functools,os,re,urllib
from flask import (Flask, flash, Markup, redirect, render_template, request,
                   Response, session, url_for)
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache
from peewee import *
from playhouse.flask_utils import FlaskDB, get_object_or_404, object_list
from playhouse.sqlite_ext import *

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# 导入其他文件包
from config import *
from model import *

# 全局定义
site_name = app.config['SITE_NAME']

def login_required(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        if session.get('logged_in'):
            return fn(*args, **kwargs)
        return redirect(url_for('login', next=request.path))
    return inner

@app.route('/login/', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next') or request.form.get('next')
    if request.method == 'POST' and request.form.get('password') and request.form.get('name'):
        name = request.form.get('name')
        password = request.form.get('password')
        if name == app.config['ADMIN_NAME'] and password == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            session.permanent = True  # 使用cooike 来保存session
            flash('您已经成功登录.', 'success')
            return redirect(next_url or url_for('index'))
        else:
            flash('账号或密码不正确!', 'error')
    return render_template('pc/login.html', next_url=next_url,main_title='登录',site_name = site_name)

@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('login'))
    return render_template('pc/logout.html',main_title ='登出',site_name=site_name)

@app.route('/')
def index():
    search_query = request.args.get('q')
    if search_query:
        query = Post.search(search_query)
    else:
        query = Post.public().order_by(Post.timestamp.desc())

    # The `object_list` helper will take a base query and then handle
    # paginating the results if there are more than 20. For more info see
    # the docs:
    # http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#object_list
    return object_list(
        'pc/index.html',
        query,
        site_name=site_name,
        search=search_query,
        check_bounds=False)

@app.route('/new/', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        if request.form.get('title') and request.form.get('content'):
            post = Post.create(
               # slug = ,
                # 别名写入之前使用编码进行修改
                slug = re.sub('[^\w]+', '-', request.form['post_slug']),
                title=request.form['title'],
                content=request.form['content'],
                published=request.form.get('published') or False)
            flash('成功发表文章!', 'warn')
            if post.published:
                return redirect(url_for('single', slug=post.slug))
            else:
                return redirect(url_for('edit', slug=post.slug))
        else:
            flash('所有项目均为必填项!', 'error')
    return render_template('pc/new.html',main_title='新增文章',site_name=site_name)

@app.route('/drafts/')
@login_required
def drafts():
    query = Post.drafts().order_by(Post.timestamp.desc())
    return object_list('pc/index.html', query, check_bounds=False)

@app.route('/<slug>/')
def single(slug):
    if session.get('logged_in'):
        query = Post.select()
    else:
        query = Post.public()
    post = get_object_or_404(query, Post.slug == slug)
    return render_template('pc/single.html', post=post,main_title= post.title,site_name=site_name)

@app.route('/<slug>/edit/', methods=['GET', 'POST'])
@login_required
def edit(slug):
    post = get_object_or_404(Post, Post.slug == slug)
    if request.method == 'POST':
        if request.form.get('title') and request.form.get('content'):
            #post.slug = request.form['post_slug']
            post.title = request.form['title']
            post.content = request.form['content']
            post.published = request.form.get('published') or False
            post.save()

            flash('保存成功!', 'warn')
            if post.published:
                return redirect(url_for('single', slug=post.slug))
            else:
                return redirect(url_for('edit', slug=post.slug))
        else:
            flash('所有项目均为必填项!', 'error')

    return render_template('pc/edit.html', post=post,main_title='编辑文章',site_name=site_name)


# 初始化结构代码,初次运行的时候产生
@app.template_filter('clean_querystring')
def clean_querystring(request_args, *keys_to_remove, **new_values):
    # 重置查询
    querystring = dict((key, value) for key, value in request_args.items())
    for key in keys_to_remove:
        querystring.pop(key, None)
    querystring.update(new_values)
    return urllib.urlencode(querystring)

@app.errorhandler(404)
def not_found(exc):
    return Response('<h3>404 Not found</h3>'), 404

def main():
    database.create_tables([Post, FTSPost], safe=True)
    app.run(debug=True)

if __name__ == '__main__':
    main()
