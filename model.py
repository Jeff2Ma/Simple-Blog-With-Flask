#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
定义核心的模块
"""

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


from config import *

class Post(flask_db.Model):
    title = CharField()
    slug = CharField(unique=True)
    content = TextField()
    published = BooleanField(index=True)
    timestamp = DateTimeField(default=datetime.datetime.now, index=True)

    @property
    def html_content(self):
        """
        Markdown 转 HTMl
        """
        hilite = CodeHiliteExtension(linenums=False, css_class='highlight')
        extras = ExtraExtension()
        markdown_content = markdown(self.content, extensions=[hilite, extras])
        oembed_content = parse_html(
            markdown_content,
            oembed_providers,
            urlize_all=True,
            maxwidth=app.config['SITE_WIDTH'])
        return Markup(oembed_content)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = re.sub('[^\w]+', '-', self.title)
        ret = super(Post, self).save(*args, **kwargs)
        self.update_search_index()
        return ret

    def update_search_index(self):
        # 保存搜索结构
        try:
            fts_post = FTSPost.get(FTSPost.post_id == self.id)
        except FTSPost.DoesNotExist:
            fts_post = FTSPost(post_id=self.id)
            force_insert = True
        else:
            force_insert = False
        fts_post.content = '\n'.join((self.title, self.content))
        fts_post.save(force_insert=force_insert)

    @classmethod
    def public(cls):
        return Post.select().where(Post.published == True)

    @classmethod
    def drafts(cls):
        return Post.select().where(Post.published == False)

    @classmethod
    def search(cls, query):
        words = [word.strip() for word in query.split() if word.strip()]
        if not words:
            # 输入的词汇无效则无返回
            return Post.select().where(Post.id == 0)
        else:
            search = ' '.join(words)

        return (FTSPost
                .select(
                    FTSPost,
                    Post,
                    FTSPost.rank().alias('score'))
                .join(Post, on=(FTSPost.post_id == Post.id).alias('post'))
                .where(
                    (Post.published == True) &
                    (FTSPost.match(search)))
                .order_by(SQL('score').desc()))

class FTSPost(FTSModel):
    post_id = IntegerField(Post)
    content = TextField()

    class Meta:
        database = database
