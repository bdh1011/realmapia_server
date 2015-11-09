# -*- coding: utf-8 -*-

from flask import current_app,Blueprint,render_template, flash,jsonify, session, url_for, g, request, redirect, make_response, Response, send_file
from app import db
from app import app
from app import redis
import hashlib, os, sys, random, re, json, ast
from functools import wraps
from datetime import date, time, datetime
import time as ptime
from flask.ext.login import login_user, logout_user, current_user, login_required
from sqlalchemy import or_, and_, desc, asc
from ..models import User, Follow, User_alert, Like, Comment, Post, Hashtag_to_post, Hashtag,\
 Placetag_to_post, Placetag, Usertag_to_post, Group, Group_member
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
import decorator
from flask_wtf.csrf import CsrfProtect

import base64
from werkzeug import secure_filename
# from forms import LoginForm

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


ALLOWED_PHOTO_EXTENSIONS = set(['png','jpg','jpeg','gif'])

ALLOWED_MOVIE_EXTENSIONS = set(['avi','mp4','mpec','exo'])


api = Blueprint('api', __name__, url_prefix='/api')
base_url = 'http://52.192.0.214/api/'

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
            print 'token!',request.headers.get('Authorization')
        # try:
            if request.headers.get('Authorization')[6:] == '1':
                session['userid'] = 'admin'
                print 'testing access'
                pass
            else:
                token = request.headers.get('Authorization')
                print 'token@',token
                if token is None:
                    return jsonify({'error':'no token headers'})
                token = token[6:]
                if app.r.get(token) is None:
                    return jsonify({'error':'token invalid'})
                print 'valid token'
                session['userid'] = ast.literal_eval(app.r.get(token))['id']
            return f(*args, **kwargs)
        # except Exception as e:
        #     print e
        #     return jsonify({'message':'unexpected error'})
    return decorated_function

@token_required
def post_profile_pic():
	profile_pic = request.json.get('photo')
	user = User.filter_by(id=session['userid']).first()
	data = base64.b64decode(photo)
	filepath = "./app/static/profile_pic/"+str(user.id)+"."+ext
	#not exist
	if not os.path.exists(filepath):
		with open(filepath,"w") as photo_file:
			photo_file.write(data)
	file_dir, filename = os.path.split(filepath)
	user.profile_pic = filename
	db.session.commit()
	#test
	return jsonify({'result':{'profile_pic_path':base_url+'profile_pic/'+filename}})

def login():
    if request.method=='POST':
        login_id = request.json.get('id')
        login_pw = request.json.get('pw')

        user = User.query.filter_by(id=login_id).first()
        if user is None:
            return jsonify({'message':'user not exist'}),400
        else:
            print user.serialize
        user.recent_login_timestamp = datetime.now()
        db.session.commit()

        try:
            if not user.verify_password(login_pw):
                raise ValueError('Could not find correct user!')
        except:
            return jsonify({'message':'id or pw is invalid'}),400

        token = user.generate_auth_token()

        print ptime.time()
        now = int(ptime.time())
        expires = now + (current_app.config['ONLINE_LAST_MINUTES'] * 600) + 10
        p = app.r.pipeline()

        if app.r.get(token) is None:
            p.set(token,{'id':user.id, 'time':int(ptime.time())})
        p.expireat(token, expires)
        p.execute()

        print 'app.r', ast.literal_eval(app.r.get(token))['id']
        #redis.flushdb() 

        return jsonify({'result':{'token':token,'name':user.name,'profile_pic':base_url+'profile_pic/'+user.profile_pic if user.profile_pic is not None else None}})


def register():
    db.session.rollback()
    register_id = request.json.get('id')
    register_name = request.json.get('name')
    register_pw = request.json.get('pw')
    print 'id :', register_id
    print 'pw :', register_pw
    if register_id is None or register_pw is None:
        return jsonify({'message':'missing arguments'}), 400
    if User.query.filter_by(id=register_id).first() is not None:
        return jsonify({'message':'existing user'}), 400

    user = User(id=register_id, name=register_name)
    user.hash_password(register_pw)

    db.session.add(user)
    db.session.commit()
    g.user = user
    token = user.generate_auth_token()
    return jsonify({ 'result': {'token':token,'name':user.name}}), 200
            # {'Location': url_for('get_user', id=user.username, _external=True)})




@token_required
def logout():
    token = request.headers.get('Authorization')
    

    if token is None:
        print 'token is None'
        return jsonify({'message':'no token headers'}),400
    print 'token is not None'
    token = token[6:]
    if app.r.get(token) is not None:
        app.r.delete(token)
    else:
        return jsonify({'message':'token invalid'}),400

    return jsonify({'result':'success'})



def filter_get_user_list(each_user, request):
    query_user_name = request.args.get('name')

    if query_user_name is not None:
        if not query_user_name in each_user.name:
            return False
    return True

#mobile api
@token_required
def get_user_list():
    try:
        user_list = [each_user.serialize for each_user in User.query.order_by(User.id).all() if filter_get_user_list(each_user,request) ]
    except:
        return jsonify({'message':'unexpected exception'}),400    
    return jsonify({'result':user_list})

#mobile api
@token_required
def get_user(userid):
    try:
        user = User.query.filter_by(id=userid).first()
    except:
        return jsonify({'message':'unexpected exception'}),400    
    return jsonify({'result':user.serialize})




@token_required
def about_me():
    my_info = User.query.filter_by(id=session['userid']).first()
    if my_info is None:
        return jsonify({'message':'login first'}),400
    return jsonify({'result':my_info.serialize})


@token_required
def get_my_posts():
    return jsonify({'result':'hi'})


@token_required
def get_my_post(post_id):
    return jsonify({'result':'hi'})


@token_required
def get_posts():
    map_type=request.args.get('map_type')
    group_name=request.args.get('group_name')
    user_id=request.args.get('user_id')
    lat=request.args.get('lat')
    lng=request.args.get('lng')
    level=request.args.get('level')

    get_posts_query = db.session.query(Post).filter(Post.map_type==map_type)
    if map_type=='group':
        get_posts_query = get_posts_query.filter(Post.target_group==group_name)
    if user_id is not None:
        get_posts_query = get_posts_query.filter(Post.user_id==user_id)
    if (lat is not None) and (lng is not None) and (level is not None):
        pass #level calculate

    posts_list = get_posts_query.all()

    return jsonify({'result':[
        {
        'post_id': each_post.id,
        'profile_pic': User.query.filter_by(id=each_post.user_id).first().profile_pic if (User.query.filter_by(id=each_post.user_id).first() is not None) else None,
        'photo' : base_url+'photo/'+each_post.photo if (each_post.photo is not None) else None,
        'video' : base_url+'video/'+each_post.video if (each_post.video is not None) else None,
        'username':User.query.filter_by(id=each_post.user_id).first().name,
        'timestamp':each_post.register_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        'content':each_post.content,
        'lat':each_post.lat,
        'lng':each_post.lng,
        'placetag':db.session.query(Placetag, Placetag_to_post ).filter(Placetag_to_post.post_id==each_post.id).filter(Placetag.id==Placetag_to_post.placetag_id).with_entities(Placetag.content).first()[0],
        'hashtag_list':[hashtag.Hashtag.content for hashtag in db.session.query(Hashtag, Hashtag_to_post ).filter(Hashtag_to_post.post_id==each_post.id).filter(Hashtag.id==Hashtag_to_post.hashtag_id).all()],
        'usertag_list':[{'userid':user.id,'username':user.name} for user in db.session.query(User, Usertag_to_post ).filter(Usertag_to_post.post_id==each_post.id).filter(User.id==Usertag_to_post.user_id).with_entities(User).all()]
        } for each_post in posts_list]})

@token_required
def get_circle():
	center_lat=request.args.get('center_lat')
	center_lng=request.args.get('center_lng')
	level=request.args.get('level')
	map_type=request.args.get('map_type')
	group_name=request.args.get('group_name')
	if map_type is None or center_lng is None or center_lng is None or level is None:
		return jsonify({'message':'parameter miss, needs center_lat, center_lng, level, map_type'}),400

	get_circle_query = db.session.query(Post).filter(Post.map_type==map_type)
	if map_type=='group':
		get_circle_query = get_circle_query.filter(Post.group_name==group_name)
	get_circle_query.filter(Post.lat.between(float(center_lat)-0.1,float(center_lat)+0.1 ))
	get_circle_query.filter(Post.lng.between(float(center_lng)-0.1,float(center_lng)+0.1 ))
	posts_list = get_circle_query.all()

	return jsonify({'result':[
		{
		'circle_id': each_post.id,
		'center_lat':each_post.lat,
		'center_lng':each_post.lng,
		'radius': 1
		} for each_post in posts_list]})

@token_required
def get_post(post_id):
	post = Post.query.filter_by(id=post_id).first()
	if post is None:
		return jsonify({'message':'wrong post id'}),404

	placetag = db.session.query(Placetag).filter(Placetag_to_post.post_id==post_id).filter(Placetag.id==Placetag_to_post.placetag_id).with_entities(Placetag.content).first()
	if placetag is not None:
		placetag = placetag[0]
	hashtag_list = [hashtag.content for hashtag in db.session.query(Hashtag).filter(Hashtag_to_post.post_id==post_id).filter(Hashtag.id==Hashtag_to_post.hashtag_id).all()]
	usertag_list = [{'userid':user.id,'username':user.name} for user in db.session.query(User).filter(Usertag_to_post.post_id==post_id).filter(User.id==Usertag_to_post.user_id).with_entities(User).all()]
	photo = base_url+'photo/'+post.photo if (post.photo is not None) else None
	video = base_url+'video/'+post.video if (post.video is not None) else None

	return jsonify({'result':{
		'userid':post.user_id,
		'photo':photo,
		'video':video,
		'map_type': post.map_type,
		'target_group':post.target_group,
		'timestamp':post.register_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
		'content':post.content,
		'lat':post.lat,
		'lng':post.lng,
		'placetag':placetag,
		'hashtag_list':hashtag_list,
		'usertag_list':usertag_list}})


@token_required
def post_sns_post():
	db.session.rollback()
	posts = request.json.get("posts")
	for post_id, sns_post in posts.iteritems():
		sns = sns_post.get("sns")
		content = sns_post.get("content")
		lat = sns_post.get("lat")
		lng = sns_post.get("lng")
		placetag_content = sns_post.get("placetag")
		hashtag_list = sns_post.get("hashtag")
		usertag_list = sns_post.get("usertag")
		photo = sns_post.get("photo")
		video = sns_post.get("video")
		ext = sns_post.get("ext")
		map_type = sns_post.get("map_type")
		post = Post(user_id=session['userid'],lat=lat,lng=lng,content=content,map_type=map_type, sns=sns)
		db.session.add(post)
		db.session.commit()

		if photo is not None:
			data = base64.b64decode(photo)
			filepath = app.config['                                                                                           ']+str(post.id)+"."+ext

			#not exist
			if not os.path.exists(filepath):
				with open(filepath,"w") as photo_file:
					photo_file.write(data)
			file_dir, filename = os.path.split(filepath)
			post.photo = filename
			db.session.commit()

		if video is not None:
			data = base64.b64decode(video)
			filepath = app.config['VIDEO_UPLOAD_FOLDER']+str(post.id)+"."+ext
			#not exist
			if not os.path.exists(filepath):
				with open(filepath,"w") as photo_file:
					photo_file.write(data)
			file_dir, filename = os.path.split(filepath)
			post.video = filename
			db.session.commit()

	    #add placetag
		if placetag_content is None:
			pass
		else:
			placetag = Placetag.query.filter_by(content=placetag_content).first()
			if placetag is None:
				placetag = Placetag(content=placetag_content)
				db.session.add(placetag)
				db.session.commit()
				#check if it works without commit
			placetag_to_post = Placetag_to_post(post_id=post.id,placetag_id=placetag.id)
			db.session.add(placetag_to_post)
			db.session.commit()

			placetag.update_placetaged_num()
			db.session.commit()
			#too many commit, how can I shrink it?


	    #add hashtag
		if hashtag_list is None:
			pass
		else:
			for each_hashtag in hashtag_list:
				print 'each hashtag',each_hashtag
				hashtag = Hashtag.query.filter_by(content=each_hashtag).first()
				print 'hashtag',hashtag
				if hashtag is None:
					hashtag = Hashtag(content=each_hashtag)
					db.session.add(hashtag)
					db.session.commit()
					#check if it works without commit
				hashtag_to_post = Hashtag_to_post(post_id=post.id,hashtag_id=hashtag.id)
				db.session.add(hashtag_to_post)
				db.session.commit()

				placetag.update_placetaged_num()
				db.session.commit()
			#too many commit, how can I shrink it?
	return jsonify({'result':{'posts_num':len(posts)}})


@token_required
def post_post():
	content = request.json.get("content")
	lat = request.json.get("lat")
	lng = request.json.get("lng")
	placetag_content = request.json.get("placetag")
	hashtag_list = request.json.get("hashtag")
	usertag_list = request.json.get("usertag")
	photo = request.json.get("photo")
	ext = request.json.get("ext")
	map_type = request.json.get("map_type")

	video = request.json.get("video")
	#post_to = request.json.get("post_to")

	post = Post(user_id=session['userid'],lat=lat,lng=lng,content=content,map_type=map_type)
	db.session.add(post)
	db.session.commit()


	if photo is not None:
		data = base64.b64decode(photo)
		filepath = app.config['PHOTO_UPLOAD_FOLDER']+str(post.id)+"."+ext

		#not exist
		if not os.path.exists(filepath):
			with open(filepath,"w") as photo_file:
				photo_file.write(data)
		file_dir, filename = os.path.split(filepath)
		post.photo = filename
		db.session.commit()

		'''
		with open(filepath,"r") as photo_file:
			photo_file.read()
		mp3_list.append(mp3_encoded)'''

	if video is not None:
		data = base64.b64decode(video)
		filepath = app.config['VIDEO_UPLOAD_FOLDER']+str(post.id)+"."+ext
		#not exist
		if not os.path.exists(filepath):
			with open(filepath,"w") as photo_file:
				photo_file.write(data)
		file_dir, filename = os.path.split(filepath)
		post.video = filename
		db.session.commit()

    #add placetag
	if placetag_content is None:
		pass
	else:
		placetag = Placetag.query.filter_by(content=placetag_content).first()
		if placetag is None:
			placetag = Placetag(content=placetag_content)
			db.session.add(placetag)
			db.session.commit()
			#check if it works without commit
		placetag_to_post = Placetag_to_post(post_id=post.id,placetag_id=placetag.id)
		db.session.add(placetag_to_post)
		db.session.commit()

		placetag.update_placetaged_num()
		db.session.commit()
		#too many commit, how can I shrink it?


    #add hashtag
	if hashtag_list is None:
		pass
	else:
		for each_hashtag in hashtag_list:
			print 'each hashtag',each_hashtag
			hashtag = Hashtag.query.filter_by(content=each_hashtag).first()
			print 'hashtag',hashtag
			if hashtag is None:
				hashtag = Hashtag(content=each_hashtag)
				db.session.add(hashtag)
				db.session.commit()
				#check if it works without commit
			hashtag_to_post = Hashtag_to_post(post_id=post.id,hashtag_id=hashtag.id)
			db.session.add(hashtag_to_post)
			db.session.commit()

			placetag.update_placetaged_num()
			db.session.commit()
		#too many commit, how can I shrink it?


	#add usertag
	if usertag_list is None:
		pass
	else:
		for usertag in usertag_list:
			user = User.query.filter_by(id=usertag).first()
			if user is None:
				return jsonify({'message':'wrong usertag'}),400
			usertag_to_post = Usertag_to_post(post_id=post.id,user_id=user.id)
			db.session.add(usertag_to_post)
			db.session.commit()            #too many commit, how can I shrink it?
	'''
	#set target to post
	if post_to is not None:
		print 'post_to',post_to
		for each_post_to in post_to:
			print each_post_to
			post_type = each_post_to.get('type')
			if post_type == 'group':
				post_to = Post_to(post_type="group", post_id=post.id, target_group=each_post_to.get('target_group'))
				db.session.add(post_to)
			elif post_type != 'private':
				post_to = Post_to(post_type=post_type, post_id=post.id)
				db.session.add(post_to)
			if Post_to.query.filter_by(post_type="private",post_id=post.id).first() is None:
				private_post_to = Post_to(post_type="private", post_id=post.id)
				db.session.add(private_post_to)
			db.session.commit()'''

	return jsonify({'result':{'post_id':post.id}})


def get_profile_pic(userid):
	user = User.query.filter_by(id=userid).first()
	if user is not None:
		if user.profile_pic is not None:
			return send_file(app.config['PROFILE_PIC_DOWNLOAD_FOLDER']+user.profile_pic )
	return jsonify({'message':'no profile picture'}),404

def get_my_profile_pic():
	profile_pic = User.query.filter_by(id=session['userid']).first().profile_pic
	if profile_pic is not None:
	    return send_file(app.config['PROFILE_PIC_DOWNLOAD_FOLDER']+profile_pic)
	return jsonify({'message':'no profile picture'}),404    

def get_photo(filename):
	root_dir = os.path.dirname(os.getcwd())
	return send_file( app.config['PHOTO_DOWNLOAD_FOLDER']+filename)

def get_movie(filename):
   return send_file(app.config['PHOTO_DOWNLOAD_FOLDER']+filename)


@token_required
def get_comments():
    print 'get comment'
    post_id = request.args.get('post_id')
    print 'post id',post_id
    user_id = request.args.get('user_id')
    name = request.args.get('name')
    
    get_comments_query = []
    if post_id is not None:
        get_comments_query.append(Comment.post_id==post_id)
    if user_id is not None:
        get_comments_query.append(Comment.user_id==user_id)
    if name is not None:
        get_comments_query.append(User.name.contains(name))
    comments_list = db.session.query(Comment).outerjoin(User).filter(and_(
                    *get_comments_query)).order_by(Comment.id).all()

    return jsonify({'result':[{
        'post_id':comment.post_id,
        'user_id':comment.user_id,
        'name': User.query.filter_by(id=comment.user_id).first().name,
        'profile_pic':User.query.filter_by(id=comment.user_id).first().profile_pic,
        'content':comment.content,
        'timestamp':comment.register_timestamp.strftime("%Y-%m-%d %H:%M:%S")} for comment in comments_list]})

@token_required
def post_comment():
    postid = request.json.get('post_id')
    content = request.json.get('content')
    post = Post.query.filter_by(id=postid)
    if post is None:
        return jsonify({'message':'invalid post id'}),400
    comment = Comment(user_id=session['userid'],post_id=postid,content=content)
    db.session.add(comment)
    db.session.commit()

    return jsonify({'result':'success'})


@token_required
def get_follow():
    from_user_id = request.args.get('from_user_id')
    to_user_id = request.args.get('to_user_id')

    if from_user_id is not None:
        follow_list = Follow.query.filter_by(from_user_id=from_user_id).all()
    if to_user_id is not None:
        follow_list = Follow.query.filter_by(to_user_id=to_user_id).all()
    return jsonify({'result': [follow.serialize for follow in follow_list]})

@token_required
def post_follow():
    to_user_id = request.json.get('to_user_id')
    if Follow.query.filter_by(from_user_id=session['userid'],to_user_id=to_user_id).first() is not None:
        return jsonify({'message':'already following'}),400
    follow = Follow(from_user_id=session['userid'],to_user_id=to_user_id)
    db.session.add(follow)
    db.session.commit()
    return jsonify({'result':'success'})


@token_required
def delete_follow():
    to_user_id = request.args.get('to_user_id')
    follow = Follow.query.filter_by(from_user_id=session['userid'],to_user_id=to_user_id).first() 
    db.session.delete(follow)
    db.session.commit()
    return jsonify({'result': 'success'})



@token_required
def get_alert():
    return jsonify({'result':'hi'})

@token_required
def get_like():
    user_id = request.args.get('user_id')
    post_id = request.args.get('post_id')
    if user_id is not None:
        like_list = Like.query.filter_by(user_id=user_id).all()
    if post_id is not None:
        like_list = Like.query.filter_by(post_id=post_id).all()

    return jsonify({'result':[ like.serialize for like in like_list ]})


@token_required
def get_hashtag(hashtag_query):
    hashtag_list = db.session.query(Hashtag).filter(Hashtag.content.contains(hashtag_query)).all()
    return jsonify({'result':[ hashtag.serialize for hashtag in hashtag_list ]})


@token_required
def get_placetag(placetag_query):
    placetag_list = db.session.query(Placetag).filter(Placetag.content.contains(placetag_query)).all()
    return jsonify({'result':[ placetag.serialize for placetag in placetag_list ]})

@token_required
def get_all_hashtag():
    hashtag_list = db.session.query(Hashtag).all()
    return jsonify({'result':[ hashtag.serialize for hashtag in hashtag_list ]})

@token_required
def get_all_placetag():
    placetag_list = db.session.query(Placetag).all()
    return jsonify({'result':[ placetag.serialize for placetag in placetag_list ]})

@token_required
def post_like():
    post_id = request.json.get('post_id')
    if Like.query.filter_by(user_id=session['userid'], post_id=post_id).first() is not None:
        return jsonify({'message':'already like it'})
    like = Like(user_id=session['userid'], post_id=post_id)
    db.session.add(like)
    db.session.commit()
    return jsonify({'result':'success'})

@token_required
def delete_like():
    user_id = request.args.get('user_id')
    post_id = request.args.get('post_id')
    like = Like.query.filter_by(user_id=user_id,post_id=post_id).first()
    db.session.delete(like)
    db.session.commit()
    return jsonify({'result':'success'})


@token_required
def get_groups():
    name = request.args.get('name')
    member = request.args.get('member')
    # print Group.query.filter_by(name=name).all()
    get_groups_query = db.session.query(Group).join(Group_member).distinct(name)
    # print get_groups_query.all()
    if member is not None:
        get_groups_query = get_groups_query.filter(Group_member.user_id==member).filter(Group.name==Group_member.group_name)

    if name is not None:
        get_groups_query = get_groups_query.filter(Group.name.contains(name))

    group_list = get_groups_query.all()
    print group_list

    return jsonify({'result':[
        {'name':group.name,
        'members':[user.user_id for user in Group_member.query.filter_by(group_name=group.name).with_entities(Group_member.user_id).all()],
        'privacy':group.privacy,
        } for group in group_list ]})


@token_required
def get_group(group_name):
    group= db.session.query(Group).join(Group_member).filter(Group.name==group_name).first()
    
    return jsonify({'result':{'name':group.name,
        'members':[user.user_id for user in Group_member.query.filter_by(group_name=group.name).with_entities(Group_member.user_id).all()],
        'privacy':group.privacy,
        }})


@token_required
def post_group():
    name = request.json.get('name')
    members = request.json.get('members')
    privacy = request.json.get('privacy')
    if Group.query.filter_by(name=name).first() is not None:
        return jsonify({'message':'group name already exist'}),400
    group = Group(name=name, privacy=privacy)
    db.session.add(group)
    member = Group_member(role='manager',user_id=session['userid'],group_name=name)
    db.session.add(member)
    for each_member in members:
        member = Group_member(user_id=each_member, role='member',group_name=name)
        db.session.add(member)
    db.session.commit()
    db.session.rollback()

    return jsonify({'result':'success'})


@token_required
def invite_group_member(group_name):
    member_list = request.json.get('members')
    for each_member in member_list:
        if Group_member.query.filter_by(group_name=group_name, user_id=each_member) is not None:
            pass
        else:
            group_member = Group_member(group_name=group_name, user_id=each_member)
            db.session.add(group_member)
            db.session.commit()

    return jsonify({'result':'success'})


@token_required
def delete_group():
    group_name = request.args.get('group_name')
    member_list = Group_member.query.filter_by(group_name = group_name).all()
    for each_member in member_list:
        db.session.delete(each_member)
    group = Group.query.filter_by(group_name=group_name).first()
    db.session.delete(group)
    db.session.commit()
    return jsonify({'result':'success'})


api.add_url_rule('/users/register', 'register', register, methods=['POST']) 
api.add_url_rule('/users/login', 'login', login, methods=['POST']) 
api.add_url_rule('/users/logout', 'logout', logout, methods=['GET']) 
api.add_url_rule('/users', 'get_user_list', get_user_list) 
api.add_url_rule('/users/<userid>', 'get_user', get_user) 

api.add_url_rule('/users/me', 'about me', about_me) 
api.add_url_rule('/users/me/profile_pic', 'post profile pic', post_profile_pic, methods=['POST'])
api.add_url_rule('/users/me/posts', 'get my posts', get_my_posts) 
api.add_url_rule('/users/me/posts/<post_id>', 'get my post', get_my_post) 

api.add_url_rule('/posts', 'get posts', get_posts, methods=['GET']) 
api.add_url_rule('/posts/<post_id>', 'get post', get_post, methods=['GET']) 
api.add_url_rule('/posts', 'post posts', post_post, methods=['POST']) 
api.add_url_rule('/sns/posts', 'post sns posts', post_sns_post, methods=['POST']) 
api.add_url_rule('/circle', 'get cicles', get_circle, methods=['GET']) 

api.add_url_rule('/profile_pic/<filename>','get profile_pic', get_profile_pic, methods=['GET'])
api.add_url_rule('/photo/<filename>','get photo', get_photo, methods=['GET'])
api.add_url_rule('/movie/<filename>','get movie', get_movie, methods=['GET'])


api.add_url_rule('/hashtag/<hashtag_query>','get hashtag', get_hashtag, methods=['GET'])
api.add_url_rule('/placetag/<placetag_query>','get placetag', get_placetag, methods=['GET'])
api.add_url_rule('/hashtag','get all hashtag', get_all_hashtag, methods=['GET'])
api.add_url_rule('/placetag','get all placetag', get_all_placetag, methods=['GET'])


api.add_url_rule('/comments', 'get comments', get_comments, methods=['GET']) 
api.add_url_rule('/comments', 'post comments', post_comment, methods=['POST']) 

api.add_url_rule('/follow', 'get following', get_follow, methods=['GET']) 
api.add_url_rule('/follow', 'post following', post_follow, methods=['POST']) 
api.add_url_rule('/follow', 'quit following', delete_follow, methods=['DELETE']) 

api.add_url_rule('/alert', 'get alert', get_alert, methods=['GET']) 

api.add_url_rule('/like', 'get like', get_like, methods=['GET']) 
api.add_url_rule('/like', 'post like', post_like, methods=['POST']) 
api.add_url_rule('/like', 'delete like', delete_like, methods=['DELETE']) 

api.add_url_rule('/groups', 'get groups', get_groups, methods=['GET']) 
api.add_url_rule('/groups/<group_name>', 'get group', get_group, methods=['GET']) 
api.add_url_rule('/groups', 'post groups', post_group, methods=['POST']) 
api.add_url_rule('/groups/<group_name>/members', 'invite group member', invite_group_member, methods=['POST']) 
api.add_url_rule('/groups/<group_name>', 'delete group', delete_group, methods=['DELETE']) 
