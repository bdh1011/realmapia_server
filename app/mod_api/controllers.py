# -*- coding: utf-8 -*-

from flask import current_app,Blueprint,render_template, flash,jsonify, session, url_for, g, request, redirect, make_response, Response
from app import db
from app import redis
import hashlib, os, sys, random, re, json, ast
from functools import wraps
from datetime import date, time, datetime
import time as ptime
from flask.ext.login import login_user, logout_user, current_user, login_required
from sqlalchemy import or_, and_, desc, asc
from ..models import User, Follow, User_alert, Like, Comment, Photo, Movie, Post, Hashtag_to_post, Hashtag,\
 Placetag_to_post, Placetag, Usertag_to_post, Post_to, Group, Group_member
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
import decorator
from flask_wtf.csrf import CsrfProtect
import app
# from forms import LoginForm

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


api = Blueprint('api', __name__, url_prefix='/api')


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




def login():
    if request.method=='POST':
        login_id = request.json.get('id')
        login_pw = request.json.get('pw')

        user = User.query.filter_by(id=login_id)
        if user is None:
            return jsonify({'message':'user not exist'}),400
        else:
            user = user.first()
        user.recent_login_timestamp = datetime.now()
        db.session.commit()

        try:
            if not user.verify_password(login_pw):
                raise ValueError('Could not find correct user!')
        except:
            return jsonify({'message':'id or pw is invalide'}),400

        token = user.generate_auth_token()

        print ptime.time()
        now = int(ptime.time())
        expires = now + (current_app.config['ONLINE_LAST_MINUTES'] * 60) + 10
        p = app.r.pipeline()

        if app.r.get(token) is None:
            p.set(token,{'id':user.id, 'time':int(ptime.time())})
        p.expireat(token, expires)
        p.execute()

        print 'app.r', ast.literal_eval(app.r.get(token))['id']
        #redis.flushdb() 

        return jsonify({'result':{'token':token,'name':user.name,'profile_pic_filename':user.profile_pic_filename}})


def register():
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
    return jsonify({ 'result': {'token':token}}), 200
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
    return jsonify({'result':'hi'})


@token_required
def get_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    placetag = db.session.query(Placetag, Placetag_to_post ).filter(Placetag_to_post.post_id==post_id).filter(Placetag.id==Placetag_to_post.placetag_id).with_entities(Placetag.content).first()[0]
    hashtag_list = [hashtag.Hashtag.content for hashtag in db.session.query(Hashtag, Hashtag_to_post ).filter(Hashtag_to_post.post_id==post_id).filter(Hashtag.id==Hashtag_to_post.hashtag_id).all()]
    usertag_list = [{'userid':user.id,'username':user.name} for user in db.session.query(User, Usertag_to_post ).filter(Usertag_to_post.post_id==post_id).filter(User.id==Usertag_to_post.user_id).with_entities(User).all()]
    return jsonify({'result':{
        'userid':post.user_id,
        'timestamp':post.register_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        'content':post.content,
        'lat':post.lat,
        'lng':post.lng,
        'placetag':placetag,
        'hashtag_list':hashtag_list,
        'usertag_list':usertag_list}})


@token_required
def post_post():
    content = request.json.get("content")
    lat = request.json.get("lat")
    lng = request.json.get("lng")
    placetag_content = request.json.get("placetag")
    hashtag_list = request.json.get("hashtag")
    usertag_list = request.json.get("usertag")
    photo = request.json.get("photo")
    movie = request.json.get("movie")
    post_to = request.json.get("post_to")

    post = Post(user_id=session['userid'],lat=lat,lng=lng,content=content)
    db.session.add(post)
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

    #set target to post
    if post_to is not None:
        print 'post_to',post_to
        for each_post_to in post_to:
            print each_post_to
            post_type = each_post_to.get('type')
            if post_type == 'group':
                post_to = Post_to(post_type="group", post_id=post.id, target_group=each_post_to.get('target_group'))
                db.session.add(post_to)
                db.session.commit()
                db.session.rollback()
            else:
                post_to = Post_to(post_type=post_type, post_id=post.id)
                db.session.add(post_to)
                db.session.commit()

    return jsonify({'result':'success'})


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
    comments_list = db.session.query(Comment, User).filter(and_(
                    *get_comments_query)).order_by(Comment.id).all()
    return jsonify({'result':[{
        'post_id':comment.Comment.post_id,
        'user_id':comment.Comment.user_id,
        'name':comment.User.name,
        'profile_pic':comment.User.profile_pic_filename,
        'content':comment.Comment.content,
        'timestamp':comment.Comment.register_timestamp} for comment in comments_list]})

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
def get_following():
    return jsonify({'result':'hi'})


@token_required
def post_following():
    return jsonify({'result':'hi'})

@token_required
def get_alert():
    return jsonify({'result':'hi'})

@token_required
def get_like():
    return jsonify({'result':'hi'})

@token_required
def post_like():
    return jsonify({'result':'hi'})


@token_required
def get_groups():
    return jsonify({'result':'hi'})


@token_required
def get_group():
    return jsonify({'result':'hi'})


@token_required
def post_group():
    return jsonify({'result':'hi'})


@token_required
def invite_group_member():
    return jsonify({'result':'hi'})


@token_required
def delete_group():
    return jsonify({'result':'hi'})



# @token_required
# def get_rooms():
#     state = request.args.get('state')
#     room_num = request.args.get('room_num')
#     cleaner_id = request.args.get('cleaner_id') 
#     supervisor_id = request.args.get('supervisor_id')

#     if len(request.args) != 0:
#         room_query = []
#         if room_num is not None:
#             #room_query.append(db.session.query(Room).filter(Room.number==room_num))
#             room_query.append(Room.number==room_num)
#         if state is not None:
#             room_query.append(Room.state.contains(state))
#         if cleaner_id is not None:
#             room_query.append(Assign.user_id.contains(cleaner_id))
#         if supervisor_id is not None:
#             room_query.append(Inspect.user_id.contains(supervisor_id))
#         print 'room_list query start'
#         room_list = db.session.query(Room).outerjoin(Reserve).outerjoin(Assign).outerjoin(Inspect).filter(and_(
#                     *room_query)).order_by(Room.number).all()
#         print 'room_list query completed'
#     else:
#         room_list = Room.query.order_by(Room.number).all()        

#     room_json_list = []
#     for each_room in room_list:
#         room_json = {}
#         room_json['room_number'] = each_room.number
#         room_json['room_type'] = each_room.room_type
#         room_json['state'] = each_room.state
#         if each_room.assign.first() is not None:
#             room_json['cleaner_id'] = each_room.assign.first().user_id
#             room_json['inspect_assigned_datetime'] = each_room.assign.first().register_timestamp.strftime("%Y-%m-%d %H:%M:%S")
#             room_json['assign_id'] = each_room.assign.first().id
#             room_json['clean_assigned_datetime'] = each_room.assign.first().register_timestamp.strftime("%Y-%m-%d %H:%M:%S")
#         if each_room.inspect.first() is not None:
#             room_json['evaluator_id'] = each_room.inspect.first().user_id
#         if each_room.reserve.first() is not None: 
#             '''
#             if each_room.reserve.first().notice is not None:
#                 room_json['notice'] = each_room.reserve.first().notice
#             '''
#             if each_room.reserve.first().checkin_time is not None:
#                 room_json['checkin_time'] = each_room.reserve.first().arrival_date.strftime("%Y-%m-%d ")+each_room.reserve.first().checkin_time.strftime("%H:%M:%S")
#                 print room_json['checkin_time']
#             if each_room.reserve.first().checkout_time is not None:
#                 room_json['checkout_time'] = each_room.reserve.first().departure_date.strftime("%Y-%m-%d ")+each_room.reserve.first().checkout_time.strftime("%H:%M:%S")
#             if each_room.reserve.first().arrival_date is not None:
#                 room_json['arrival_date'] = each_room.reserve.first().arrival_date.strftime("%Y-%m-%d %H:%M:%S")
#             if each_room.reserve.first().departure_date is not None:
#                 room_json['departure_date'] = each_room.reserve.first().departure_date.strftime("%Y-%m-%d %H:%M:%S")
#         room_json_list.append(room_json)
#     return jsonify({'result':room_json_list})

# @token_required
# def evaluation(**kwargs):
#     if request.method == 'GET':
#         cleaner_id = request.args.get('cleaner_id')
#         evaluator_id = request.args.get('evaluator_id')
#         description = request.args.get('description')
#         room_num = request.args.get('room_num')
#         evaluation_query = []
#         if cleaner_id is not None:
#             evaluation_query.append(db.session.query(Assign).filter(Assign.user_id==cleaner_id))
#         if evaluator_id is not None:
#             evaluation_query.append(db.session.query(Inspect).filter(Inspect.user_id==evaluator_id))
#         if description is not None:
#             evaluation_query.append(db.session.query(Inspection_form).filter(Inspection_form.contains(description)))
#         if room_num is not None:
#             evaluation_query.append(db.session.query(Inspect).filter(Inspect.room_num==room_num))

#         evaluation_list = db.session.query(Evaluation).join(Assign).join(Inspect).filter(and_(
#             *evaluation_query)).order_by(Evaluation.id).all()

#         evaluation_json_list = []
#         for each_evaluation in evaluation_list:
#             evaluation_json = {}
#             evaluation_json['id'] = each_evaluation.id
#             evaluation_json['timestamp'] = each_evaluation.timestamp.strftime("%Y-%m-%d %H:%M:%S")
#             evaluation_json['point'] = each_evaluation.check
#             evaluation_json['comment'] = each_evaluation.comment
#             inspection_form = Inspection_form.query.filter_by(id=each_evaluation.inspection_form_id).first()
#             if inspection_form is not None:
#                 evaluation_json['form_id'] = inspection_form.id
#                 evaluation_json['form_type'] = inspection_form.form_type
#                 evaluation_json['form_num'] = inspection_form.form_num
#                 evaluation_json['description'] = inspection_form.description
#                 evaluation_json['total_point'] = inspection_form.total_point
#             else:
#                 return jsonify({'message':'inspection form id is invalid'}),400
#             assign = Assign.query.filter_by(id=each_evaluation.assign_id).first()
#             if assign is not None:
#                 evaluation_json['cleaner_id'] = assign.user_id
#                 evaluation_json['room_num'] = assign.room_num
#                 evaluation_json['evaluator_id'] = assign.user_id
#             evaluation_json_list.append(evaluation_json)

#         return jsonify({'result':evaluation_json_list})
#     else:
#         room_num = int(request.json.get("room_num"))
#         evaluation_type = request.json.get("type")
#         evaluation_form_dict = request.json.get("inspection_form_dict")
#         inspection_form = Inspection_form.query.filter_by(form_type=evaluation_type).order_by(Inspection_form.form_num)
#         form_len = len(inspection_form.all())
#         sent_form_len = len(evaluation_form_dict)
#         if form_len != sent_form_len:
#             return jsonify({'message':'You must check whole forms. There are '+str(form_len)+' forms and you checked '+str(sent_form_len)+' forms'}),400
       

#         #have to add assigned day filter
#         assign = Assign.query.filter_by(room_num=room_num).order_by(Assign.register_timestamp).first()
#         assign_id = None
#         if assign is not None:
#             assign_id = int(assign.id)
#         else:
#             return jsonify({'message':'not assigned room'}),400
#         #have to add evaluator's id filter 
#         inspect = Inspect.query.filter_by(room_num=room_num).order_by(Inspect.register_timestamp).first()
#         inspect_id = None
#         if inspect is not None:
#             inspect_id = inspect.id
#         else:
#             return jsonify({'message':'not assigned inspection'}),400
        
#         received_point = 0
#         total_point = 0
#         for form_id, evaluation_dict in evaluation_form_dict.iteritems():
#             check = evaluation_dict['check']
#             comment = evaluation_dict.get('comment')
#             form = inspection_form.filter_by(id=form_id).first()
#             if form is None:
#                 return jsonify({'message':'form id is invalid'}),400
#             form_point = form.total_point
#             if check == True:
#                 received_point += form_point
#             total_point += int(form_point)

#             evaluation = Evaluation(comment=comment,check=check, inspection_form_id=int(form_id), assign_id=assign_id, inspect_id=inspect_id)
#             db.session.add(evaluation)
#             db.session.commit()
#             db.session.flush()
#         # inspect.total_point = total_point
#         inspect.received_point = received_point
#         db.session.commit()
#         db.session.rollback()
#         return jsonify({'result':{'total_point':total_point, 'received_point':received_point}})#will be implement later


# @token_required
# def add_form():
#     form_type = request.json.get('form_type')
#     form_num = request.json.get('form_num') 
#     form_description = request.json.get('form_description')
#     form_total_point = request.json.get('form_total_point')
#     form_id = request.json.get('form_id')

#     if form_id is not None:
#         inspection_form = Inspection_form.query.filter_by(id=int(form_id)).first()
#         inspection_form.form_type = form_type
#         inspection_form.form_num = int(form_num)
#         inspection_form.form_description = form_description
#         inspection_form.form_total_point = int(form_total_point)
#     else:
#         inspection_form = Inspection_form(form_type=form_type, form_num=form_num, description=form_description, total_point=form_total_point)
#         db.session.add(inspection_form)

#     db.session.commit()
#     return jsonify({'result':'success'})


# @api.route('/form')
# def get_form(**kwargs):
#     form_id = kwargs.get('form_id')
#     form_type = request.args.get('form_type')
#     form_num =  request.args.get('form_num')
#     form_description =  request.args.get('description')
#     form_total_point =  request.args.get('total_point')

#     if form_id is not None:
#         inspection_form_list = Inspection_form.query.filter_by(id=form_id).all()
#     else:
#         inspection_form_list = Inspection_form.query.order_by(Inspection_form.form_type.desc(), Inspection_form.form_num.asc()).all()
    
#     inspection_form_json_list = []
#     for each_inspection_form in inspection_form_list:
#         if form_type is not None:
#             if form_type != each_inspection_form.form_type:
#                 continue
#         if form_num is not None:
#             if int(form_num) != each_inspection_form.form_num:
#                 continue
#         if form_description is not None:
#             if form_description != each_inspection_form.description:
#                 continue
#         if form_total_point is not None:
#             if int(form_total_point) != each_inspection_form.total_point:
#                 continue

#         inspection_form_json = {}
#         inspection_form_json['id'] = int(each_inspection_form.id)
#         inspection_form_json['form_type'] = each_inspection_form.form_type
#         inspection_form_json['form_num'] = int(each_inspection_form.form_num)
#         inspection_form_json['description'] = each_inspection_form.description
#         inspection_form_json['total_point'] = each_inspection_form.total_point
#         inspection_form_json_list.append(inspection_form_json)

#     return jsonify({'result':inspection_form_json_list})

# @token_required
# def requirements(room_num):
#     if request.method == 'GET':
#         reserve = Reserve.query.filter_by(room_num=room_num).first()
#         if reserve is not None:
#             return jsonify({'result':reserve.requirement})
#         else:
#             return jsonify({'result':''})
#     else:
#         reserve = Reserve.query.filter_by(room_num=room_num).first()
#         print 'reserve',reserve
#         if reserve is not None:
#             reserve.requirement = request.json['requirement']
#         else:
#             return jsonify({'message':'not reserved room'})
#         db.session.commit()
#         db.session.rollback()

#         return jsonify({'result':'success'})

# @token_required
# def walkie_channel(**kwargs):
#     walkie_channel_id = kwargs.get('channel_id')
#     if walkie_channel_id is not None:
#         walkie_channel_list = Walkie_channel.query.filter_by(id=walkie_channel_id).all()
#         if walkie_channel_list is None:
#             return jsonify({'message':'channel not exist'}),400
#     else:
#         walkie_query = []
#         walkie_channel_member = request.args.get('joined_member')
#         walkie_channel_name = request.args.get('channel_name')
#         #print walkie_query
#         if walkie_channel_name is not None:
#             print 'channel name', walkie_channel_name
#             walkie_query.append((Walkie_channel.channel_name.contains(walkie_channel_name)))
#         if walkie_channel_member is not None:
#             walkie_query.append((Walkie_member.member_id==walkie_channel_member))

#         if len(walkie_query) > 0:

#             walkie_channel_list = db.session.query(Walkie_channel).join(Walkie_member).filter(and_(*walkie_query)).order_by(Walkie_channel.id).all()
#         else:
#             walkie_channel_list = db.session.query(Walkie_channel).join(Walkie_member).order_by(Walkie_channel.id).all()

#         print len(walkie_channel_list)

#     return jsonify({'result':[{'channel_id': each_channel.id,
#         'channel_name':each_channel.channel_name,
#         'member_list': [each_member.member_id for each_member in Walkie_member.query.filter_by(channel_id=each_channel.id)],
#         'host_id':each_channel.host_id} for each_channel in walkie_channel_list]})


# @token_required
# def make_channel():
#     print request.data
#     channel_name = request.json.get('channel_name')
#     members_list = request.json.get('member_list')
#     print 'channel name', channel_name
#     print 'members_list', members_list

#     if session['userid'] not in members_list:
#         members_list.append(session['userid'])
#     walkie_channel = Walkie_channel(channel_name=channel_name, host_id=session['userid'])
#     db.session.add(walkie_channel)
#     db.session.commit()
#     db.session.flush()
#     for each_member in members_list:
#         print each_member
#         if User.query.filter_by(id=each_member).first() is None:
#             return jsonify({'message':'there is wrong user id'}),400
#         walkie_member = Walkie_member(channel_id=walkie_channel.id, member_id=each_member)
#         db.session.add(walkie_member)
#     db.session.commit()
#     db.session.flush()
#     return jsonify({'result':{'channel_id':walkie_channel.id,
#         'channel_name':walkie_channel.channel_name,
#         'member_list':members_list,
#         'host_id':session['userid']}})


# def RepresentsInt(s):
#     try: 
#         int(s)
#         return True
#     except ValueError:
#         return False



# @token_required
# def delete_channel(channel_id):
#     print 'channel id',channel_id
#     channel = Walkie_channel.query.filter_by(id=channel_id).first()
#     if channel is not None:
#         if channel.host_id == session['userid']:
#             db.session.delete(channel)
#             db.session.commit()
#             return jsonify({'result':'success'})
#         return jsonify({'message':'only host can delete a channel'}),403
#     else:
#         return jsonify({'message':'wrong id'}),400

# @token_required
# def invite_member(channel_id):
#     channel_id = request.json.get('channel_id')
#     members_list = request.json.get('member_list')
#     print 'channel id',channel_id
#     channel = Walkie_channel.query.filter_by(id=channel_id).first()
#     if channel is not None:
#         for each_member in members_list:
#             if Walkie_member.query.filter_by(channel_id=channel_id, member_id=each_member).first() is None:
#                 walkie_member = Walkie_member(channel_id=channel_id, member_id=each_member)
#                 db.session.add(walkie_member)
#         db.session.commit()

#         return jsonify({'message':'only host can delete a channel'})
#     else:
#         return jsonify({'message':'wrong id'}),400

# @token_required
# def exit_channel(channel_id):
#     print 'channel id',channel_id
#     channel = Walkie_channel.query.filter_by(id=channel_id).first()
#     if channel is not None:
#         walkie_member = Walkie_member.query.filter_by(channel_id=channel_id, member_id=session['userid']).first()
#         if walkie_member is not None:
#             db.session.delete(walkie_member)
#             db.session.commit()
#             return jsonify({'result':'success'})
#         return jsonify({'message':'wrong value'}),400
#     else:
#         return jsonify({'message':'wrong channel id'}),400

# @token_required
# def send_message(channel_id):
#     msg = request.json.get('msg')
#     print 'size',sys.getsizeof(msg)
#     if sys.getsizeof(msg) > 2000000:
#         return jsonify({'message':'message is too large'}),400
#     print 'channel id',channel_id
#     channel = Walkie_channel.query.filter_by(id=channel_id).first()
#     if channel is not None:
#         walkie_msg = Walkie_message(member_id=session['userid'],channel_id=channel_id,msg=msg)
#         db.session.add(walkie_msg)    
#         db.session.commit()
#         return jsonify({'result':{'msg_id':walkie_msg.id,'timestamp':walkie_msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),'msg_size':sys.getsizeof(msg)}})
#     else:
#         return jsonify({'message':'wrong channel id'}),400


# @token_required
# def get_message(channel_id):
#     print 'channel id',channel_id
#     channel = Walkie_channel.query.filter_by(id=channel_id).first()
#     last_received = request.args.get('last_received')
#     walkie_message_from = request.args.get('from')
#     walkie_message_num = request.args.get('num')

#     print last_received
#     if channel is not None:
#         #temp,
#         get_msg_query = []
#         get_msg_query.append(Walkie_message.channel_id==channel_id)
#         get_msg_query.append(Walkie_message.member_id!=session['userid'])
#         if last_received is not None:
#             get_msg_query.append(Walkie_message.timestamp > datetime.strptime(last_received, "%Y-%m-%d %H:%M:%S"))
          
#         if walkie_message_from != "latest":
#             walkie_msg_list = db.session.query(Walkie_message).filter(and_
#             (*get_msg_query)).order_by(asc(Walkie_message.timestamp)).all()
#         else:
#             walkie_msg_list = db.session.query(Walkie_message).filter(and_
#             (*get_msg_query)).order_by(desc(Walkie_message.timestamp)).all()
#         print walkie_msg_list
#         #nothing to find
#         if len(walkie_msg_list)== 0 :
#             return jsonify({'result':None})

#         next_msg_num = len(walkie_msg_list)
#         if walkie_message_num is not None:
#             walkie_msg_list = walkie_msg_list[:int(walkie_message_num)]
#         else:
#             walkie_msg_list = walkie_msg_list[:1]
#         # walkie_msg = Walkie_message.query.filter_by(channel_id=channel_id).first()
        
#         return jsonify({'result':[
#             {
#             'channel_id':walkie_msg.channel_id,
#             'msg_id':walkie_msg.id,
#             'timestamp':walkie_msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
#             'msg':walkie_msg.msg,
#             'member_id':walkie_msg.member_id,
#             'next_msg_num':next_msg_num,
#             'msg_size':sys.getsizeof(walkie_msg.msg)
#             } for walkie_msg in walkie_msg_list]} )
#     else:
#         return jsonify({'message':'wrong channel id'}),400



# @token_required
# def get_polling_message():
#     last_received = request.args.get('last_received')
#     walkie_message_from = request.args.get('from')
#     walkie_message_num = request.args.get('num')

      
#     get_msg_query = []
#     if last_received is not None:
#         get_msg_query.append(Walkie_message.timestamp > datetime.strptime(last_received, "%Y-%m-%d %H:%M:%S"))
      
#     if walkie_message_from != "latest":
#         walkie_msg_list = db.session.query(Walkie_message).filter(and_
#         (*get_msg_query)).order_by(asc(Walkie_message.timestamp)).all()
#     else:
#         walkie_msg_list = db.session.query(Walkie_message).filter(and_
#         (*get_msg_query)).order_by(desc(Walkie_message.timestamp)).all()
#     print walkie_msg_list
#     #nothing to find
#     if len(walkie_msg_list)== 0 :
#         return jsonify({'result':None})

#     next_msg_num = len(walkie_msg_list)
#     if walkie_message_num is not None:
#         walkie_msg_list = walkie_msg_list[:int(walkie_message_num)]
#     else:
#         walkie_msg_list = walkie_msg_list[:1]
#     # walkie_msg = Walkie_message.query.filter_by(channel_id=channel_id).first()
    
#     return jsonify({'result':[
#         {
#         'channel_id':walkie_msg.channel_id,
#         'msg_id':walkie_msg.id,
#         'timestamp':walkie_msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
#         'msg':walkie_msg.msg,
#         'member_id':walkie_msg.member_id,
#         'next_msg_num':next_msg_num,
#         'msg_size':sys.getsizeof(walkie_msg.msg)
#         } for walkie_msg in walkie_msg_list]} )
    
api.add_url_rule('/users/register', 'register', register, methods=['POST']) 
api.add_url_rule('/users/login', 'login', login, methods=['POST']) 
api.add_url_rule('/users/logout', 'logout', logout, methods=['GET']) 
api.add_url_rule('/users', 'get_user_list', get_user_list) 
api.add_url_rule('/users/<userid>', 'get_user', get_user) 
api.add_url_rule('/users/me', 'about me', about_me) 
api.add_url_rule('/users/me/posts', 'get my posts', get_my_posts) 
api.add_url_rule('/users/me/posts/<post_id>', 'get my post', get_my_post) 

api.add_url_rule('/posts', 'get posts', get_posts, methods=['GET']) 
api.add_url_rule('/posts/<post_id>', 'get post', get_post, methods=['GET']) 
api.add_url_rule('/posts', 'post posts', post_post, methods=['POST']) 

api.add_url_rule('/comments', 'get comments', get_comments, methods=['GET']) 
api.add_url_rule('/comments', 'post comments', post_comment, methods=['POST']) 

api.add_url_rule('/following', 'get following', get_following, methods=['GET']) 
api.add_url_rule('/following', 'post following', post_following, methods=['POST']) 

api.add_url_rule('/alert', 'get alert', get_alert, methods=['GET']) 

api.add_url_rule('/like', 'get like', get_like, methods=['GET']) 
api.add_url_rule('/like', 'post like', post_like, methods=['POST']) 

api.add_url_rule('/groups', 'get groups', get_groups, methods=['GET']) 
api.add_url_rule('/groups/<group_id>', 'get group', get_group, methods=['GET']) 
api.add_url_rule('/groups', 'post groups', post_group, methods=['POST']) 
api.add_url_rule('/groups/<groupd_id>/members', 'invite group member', invite_group_member, methods=['POST']) 
api.add_url_rule('/groups/<group_id>', 'delete group', delete_group, methods=['DELETE']) 

