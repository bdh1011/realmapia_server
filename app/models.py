# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from flask import current_app

from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

import json, os, uuid
from app.database import db

def dump_datetime(value):
	if value is None:
		return None
	return value.strftime("%Y-%m-%d %H:%M:%S")


class User(db.Model):
	__tablename__ = 'user'
	id = db.Column(db.String(64), primary_key=True, nullable=False)
	password_hash = db.Column(db.String(256), nullable=True)
	name = db.Column(db.String(64), nullable=False)
	register_timestamp = db.Column(db.DateTime, server_default=db.func.now())
	recent_login_timestamp = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
	profile_pic = db.Column(db.String(64), nullable=True)
	
	facebook_token = db.Column(db.String(64),nullable=True)
	instagram_token = db.Column(db.String(64),nullable=True)
	twitter_token = db.Column(db.String(64),nullable=True)


	follow_from = db.relationship('Follow', backref='follow_from_user', foreign_keys='Follow.from_user_id', lazy='dynamic')
	follow_to = db.relationship('Follow', backref='follow_to_user', foreign_keys='Follow.to_user_id', lazy='dynamic')
	like = db.relationship('Like', backref='Like.user_id', lazy='dynamic')
	user_alert = db.relationship('User_alert', backref='User_alert.user_id', lazy='dynamic')
	comment = db.relationship('Comment', backref='Comment.user_id', lazy='dynamic')
	usertag_to_post = db.relationship('Usertag_to_post', backref='Usertag_to_post.usertag_id', lazy='dynamic')
	group_member = db.relationship('Group_member', backref='Group_member.user_id', lazy='dynamic')
	push = db.relationship('Push', backref='Push.user_id', lazy='dynamic')

	noti_from = db.relationship('Noti', backref='noti_from_user', foreign_keys='Noti.user_from', lazy='dynamic')
	noti_to = db.relationship('Noti', backref='noti_to_user', foreign_keys='Noti.user_to', lazy='dynamic')


	def __init__(self, **kwargs):
		self.id = kwargs['id']
		self.name = kwargs['name']
		if 'profile_pic_filename' in kwargs:
			self.profile_pic_filename = kwargs['profile_pic_filename']

	def hash_password(self, password):
		self.password_hash = pwd_context.encrypt(password)

	def verify_password(self, password):
		return pwd_context.verify(password, self.password_hash)

	def generate_auth_token(self, expiration=360000):
		s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
		print 'origin token', s.dumps({'id': self.id})
		
		return s.dumps({'id': self.id})



	@staticmethod
	def verify_auth_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			print 'get token',token
			data = s.loads(token)
			print data
		except SignatureExpired:
			print 'expired'
			return None    # valid token, but expired
		except BadSignature:
			return None    # invalid token
		user = User.query.get(data['id'])
		return user
	@property
	def profile_pic_url(self):
		return 'http://52.192.0.214/api/profile_pic/'+self.profile_pic if self.profile_pic is not None else None

	@property
	def serialize(self):
	    return {
	    	'id'		: self.id,
	    	'name'		: self.name,
	    	'profile_pic'  : 'http://52.192.0.214/api/profile_pic/'+self.profile_pic if self.profile_pic is not None else None,
	    	'register_timestamp'	: dump_datetime(self.register_timestamp),
	    	'recent_login_timestamp': dump_datetime(self.recent_login_timestamp)
	    }
	

class Follow(db.Model):
	__tablename__ = 'follow'
	from_user_id = db.Column(db.String(64), db.ForeignKey('user.id'),primary_key=True)
	to_user_id = db.Column(db.String(64), db.ForeignKey('user.id'),primary_key=True)
	register_timestamp = db.Column(db.DateTime, server_default=db.func.now())
	def __init__(self, **kwargs):
			super(Follow, self).__init__(**kwargs)

	@property
	def serialize(self):
	    return {
	    	'from_user_id'		: self.from_user_id,
	    	'to_user_id'		: self.to_user_id,
	    	'register_timestamp'  : dump_datetime(self.register_timestamp)
	    }
	

class User_alert(db.Model):
	__tablename__ = 'user_alert'
	id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
	user_id = db.Column(db.String(64), db.ForeignKey('user.id'))
	content = db.Column(db.Text, nullable=False)
	link = db.Column(db.String(64), nullable=True)
	register_timestamp = db.Column(db.DateTime, server_default=db.func.now())
	def __init__(self, **kwargs):
			super(User_alert, self).__init__(**kwargs)


class Like(db.Model):
	__tablename__ = 'like'
	id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
	user_id = db.Column(db.String(64), db.ForeignKey('user.id'))
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
	register_timestamp = db.Column(db.DateTime, default=db.func.now())

	def __init__(self, **kwargs):
		super(Like, self).__init__(**kwargs)

	@property
	def serialize(self):
	    return {
	    	'id'		: self.id,
	    	'user_id'		: self.user_id,
	    	'post_id'		: self.post_id,
	    	'register_timestamp'  : dump_datetime(self.register_timestamp)
	    }
	


class Comment(db.Model):
	__tablename__ = 'comment'
	id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
	user_id = db.Column(db.String(64), db.ForeignKey('user.id'))
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
	content = db.Column(db.Text)
	register_timestamp = db.Column(db.DateTime, default=db.func.now())
	recent_login_timestamp = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
	def __init__(self, **kwargs):
		super(Comment, self).__init__(**kwargs)






class Post(db.Model):
	__tablename__ = 'post'
	id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
	user_id = db.Column(db.String(64), db.ForeignKey('user.id'))
	lat = db.Column(db.Float, nullable=True)
	lng = db.Column(db.Float, nullable=True)
	photo = db.Column(db.String(64), nullable=True)
	video = db.Column(db.String(64), nullable=True)
	content = db.Column(db.Text)
	map_type = db.Column(db.String(64), nullable=True)
	target_group = db.Column(db.String(64), db.ForeignKey('group.id'))
	sns = db.Column(db.String(64), nullable=True)
	register_timestamp = db.Column(db.DateTime, default=db.func.now())
	recent_login_timestamp = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
	
	def __init__(self, **kwargs):
		super(Post, self).__init__(**kwargs)


	like = db.relationship('Like', backref='Like.post_id', lazy='dynamic')
	comment = db.relationship('Comment', backref='Comment.post_id', lazy='dynamic')
	
	hashtag_to_post = db.relationship('Hashtag_to_post', backref='Hashtag_to_post.post_id', lazy='dynamic')
	placetag_to_post = db.relationship('Placetag_to_post', backref='Placetag_to_post.post_id', lazy='dynamic')
	usertag_to_post = db.relationship('Usertag_to_post', backref='Usertag_to_post.post_id', lazy='dynamic')
	noti = db.relationship('Noti', backref='Noti.post_id', lazy='dynamic')
	



class Hashtag_to_post(db.Model):
	__tablename__ = 'hashtag_to_post'
	id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
	hashtag_id = db.Column(db.Integer, db.ForeignKey('hashtag.id'))
	register_timestamp = db.Column(db.DateTime, default=db.func.now())
	recent_login_timestamp = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
	
	def __init__(self, **kwargs):
		super(Hashtag_to_post, self).__init__(**kwargs)


class Hashtag(db.Model):
	__tablename__ = 'hashtag'
	id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
	content = db.Column(db.Text)
	hashtaged_num = db.Column(db.Integer, default=1)
	register_timestamp = db.Column(db.DateTime, default=db.func.now())
	recent_login_timestamp = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
	
	def __init__(self, **kwargs):
		super(Hashtag, self).__init__(**kwargs)

	def update_hashtaged_num(self):
		hashtaged_num = Hashtag_to_post.query.filter_by(hashtag_id=self.id).count()
		self.hashtaged_num = hashtaged_num

	@property
	def serialize(self):
	    return {
	    	'id'		: self.id,
	    	'content'		: self.content,
	    	'hashtaged_num'  : self.hashtaged_num,
	    	'register_timestamp'	: dump_datetime(self.register_timestamp),
	    	'recent_login_timestamp': dump_datetime(self.recent_login_timestamp)
	    }



class Placetag_to_post(db.Model):
	__tablename__ = 'placetag_to_post'
	id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
	placetag_id = db.Column(db.Integer, db.ForeignKey('placetag.id'))
	register_timestamp = db.Column(db.DateTime, default=db.func.now())
	recent_login_timestamp = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
	
	def __init__(self, **kwargs):
		super(Placetag_to_post, self).__init__(**kwargs)



class Placetag(db.Model):
	__tablename__ = 'placetag'
	id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
	content = db.Column(db.Text)
	placetaged_num = db.Column(db.Integer, default=1)
	register_timestamp = db.Column(db.DateTime, default=db.func.now())
	recent_login_timestamp = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
	
	def __init__(self, **kwargs):
		super(Placetag, self).__init__(**kwargs)

	def update_placetaged_num(self):
		placetaged_num = Placetag_to_post.query.filter_by(placetag_id=self.id).count()
		self.placetaged_num = placetaged_num

	@property
	def serialize(self):
	    return {
	    	'id'		: self.id,
	    	'content'		: self.content,
	    	'placetaged_num'  : self.placetaged_num,
	    	'register_timestamp'	: dump_datetime(self.register_timestamp),
	    	'recent_login_timestamp': dump_datetime(self.recent_login_timestamp)
	    }





class Usertag_to_post(db.Model):
	__tablename__ = 'usertag_to_post'
	id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
	user_id = db.Column(db.String(64), db.ForeignKey('user.id'))
	register_timestamp = db.Column(db.DateTime, default=db.func.now())
	recent_login_timestamp = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
	
	def __init__(self, **kwargs):
		super(Usertag_to_post, self).__init__(**kwargs)



class Group(db.Model):
	__tablename__ = 'group'
	id = db.Column(db.String(64), nullable=False, primary_key=True)
	privacy = db.Column(db.String(64), nullable=False)
	#privacy : privat, protected, public
	register_timestamp = db.Column(db.DateTime, default=db.func.now())
	recent_login_timestamp = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
	
	def __init__(self, **kwargs):
		super(Group, self).__init__(**kwargs)

	post = db.relationship('Post', backref='Post.id', lazy='dynamic')

class Group_member(db.Model):
	__tablename__ = 'group_member'
	role = db.Column(db.String(64), nullable=False)
	register_timestamp = db.Column(db.DateTime, default=db.func.now())
	recent_login_timestamp = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
	user_id = db.Column(db.String(64), db.ForeignKey('user.id'), nullable=False, primary_key=True)
	group_id = db.Column(db.String(64), db.ForeignKey('group.id'), nullable=False, primary_key=True)
	register_timestamp = db.Column(db.DateTime, default=db.func.now())

	def __init__(self, **kwargs):
		super(Group_member, self).__init__(**kwargs)

class Push(db.Model):
	__tablename__ = 'push'
	id = db.Column(db.String(256), nullable=False, primary_key=True)
	user_id = db.Column(db.String(64), db.ForeignKey('user.id'), nullable=False)


class Noti(db.Model):
	__tablename__ = 'noti'
	id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
	user_from = db.Column(db.String(64), db.ForeignKey('user.id'), nullable=False)
	noti_type = db.Column(db.String(64), nullable=False)
	user_to = db.Column(db.String(64), db.ForeignKey('user.id'), nullable=False, index=True)
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
	register_timestamp = db.Column(db.DateTime, default=db.func.now())

	def __init__(self, **kwargs):
		super(Noti, self).__init__(**kwargs)



