# Simple-Blog-With-Flask

>  基于Python+Flask 制作的小型简单博客应用。为本人的课程设计拙作。
>  拥有基本的登录登出、写文章、新建文章、编辑文章等功能。

## 基本构成

### 使用到的编程语言

Python、HTML、CSS、JavaScript

### 使用到的框架

Flask、peewee、jQuery、Primer

### 数据库

SQLite

## 使用方法

1. 通过`git clone` 下载本rep

		git clone https://github.com/Jeff2Ma/Simple-Blog-With-Flask
	

2. 通过虚拟沙盒方式运行激活

		virtualenv Simple-Blog-With-Flask
		cd Simple-Blog-With-Flask/
		source bin/activate
		
3. 安装相关模块
		
		pip install -r requirements.txt
		
4. 启动本地服务器

		python app.py