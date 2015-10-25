# -*- coding: utf-8 -*-
from flask import render_template, flash,jsonify, session, url_for, g, request, redirect, make_response, Response
from app import db
from app import app
from app import redis
import hashlib
import os
import sys
import random
import re
import json
import ast
from functools import wraps
from datetime import date, time, datetime
import time as ptime
from flask.ext.login import login_user, logout_user, current_user, login_required
from sqlalchemy import or_, and_
from sqlalchemy import desc, asc
from models import Employee, Room, Assign, Team, Reserve, Inspect, Inspection_form,Evaluation, Clean, Walkie_channel, Walkie_member
import decorator
# from forms import LoginForm

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print 'login required'
        if not 'userid' in session:
            return redirect(url_for('login'), next=request.url)
        user = Employee.query.filter_by(id=session['userid']).first()
        if user is None:
            print 'user is None'
            return logout()
        return f(*args, **kwargs)
    return decorated_function


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        print 'json',request.json
        if token is None:
            return jsonify({'error':'no token headers'})
        token = token[6:]
        if redis.get(token) is None:
            return jsonify({'error':'token invalid'})
        session['userid'] = ast.literal_eval(redis.get(token))['id']
        return f(*args, **kwargs)
    return decorated_function





# def mark_online(token):

#     now = int(time.time())
#     online_expires = now + (app.config['ONLINE_LAST_MINUTES'] * 60) + 10
#     session_expires = now + (app.config['SESSION_ALIVE_MINUTES'] * 60) + 10

#     userid = ast.literal_eval(redis.get(token))['id']
    
#     print 'now',now
#     print 'expires',expires

#     redis.set(token, {'id':userid, 'time':now})
#     redis.expireat(token, session_expires)

    

# def get_user_last_activity(user_id):
#     last_activity = redis.get('user-activity/%s' % user_id)
#     if last_activity is None:
#         return None
#     return datetime.utcfromtimestamp(int(last_activity))

# def get_online_users(*kwargs):
#     current = int(time.time()) // 60
#     minutes = xrange(app.config['ONLINE_LAST_MINUTES'])


#     #redis.flushall()
#     for key in redis.keys():
#         print redis.get(key)
#     if len(kwargs) != 0:
#         return redis.get(kwargs.get('employee_id'))
#     return [{'id':ast.literal_eval(redis.get(key))['id'],'now':ast.literal_eval(redis.get(key)).get('time')} for key in redis.keys() ]


# @app.route('/online/<employee_id>')
# def is_online(employee_id):
#     return jsonify({'result':get_online_users(employee_id)})



# @app.route('/online')
# def get_all_online():
#     return jsonify({'result':get_online_users()})


# @app.route('/set_online')
# def set(): 
#     mark_current_user_online()
#     return 'hi'


@app.route('/signup', methods=['POST'])
def signup():
    id = request.form['id']
    name = request.form['name']
    password =  request.form['password']
    gender = request.form['gender']
    year = request.form['year']
    month = request.form['month']
    day = request.form['day']
    birthday =  year + month + day
    position =  request.form['position']

    if id is None or password is None:
        print 'fill the form'
        return redirect(url_for('signup_page'))

    if Employee.query.filter_by(id=id).first() is not None:
        print 'id already exist'
        return redirect(url_for('signup_page'))

    if 'team' in request.form:
        team =  request.form['team']
        employee = Employee(id=id, team=team, name=name, password=password,position=position, birthday=birthday, gender=gender)
    else:
        employee = Employee(id=id, name=name, password=password,position=position, birthday=birthday, gender=gender)

    db.session.add(employee)
    db.session.commit()
    session['userid'] = employee.id
    # user_hash = hashlib.sha1(str(user.id)).hexdigest()
    # session['token'] = user_hash
    return redirect(url_for('main'))



@app.route('/signup',  methods=['GET'])
def signup_page():
    if Employee.query.filter_by(id=session.get('userid')).first() is not None:
        return redirect(url_for('main'))
    team_list = Team.query.order_by(Team.name).distinct()
    return render_template("signup.html", team_list=team_list)



@app.route('/signup/id/<id>')
def check_duplicate_id(id):
    if Employee.query.filter_by(id=id).first() is not None:
        return jsonify({'exist':'true'})
    else:
        return jsonify({'exist':'false'})


#temp popup
@app.route('/plus_pop')
def plus():
    return render_template('plus_pop.html')

@app.route('/employee_manage',methods=['GET'])
@login_required
def employee_manage():
    if 'team' in request.args:
        team = request.args['team']
        print team
        if team == 'all':
            employee_list = Employee.query.order_by(Employee.id).all()
        elif team is not None:
            employee_list = Employee.query.filter_by(team=team).order_by(Employee.id).all()
    else:
        employee_list = Employee.query.order_by(Employee.id).all()
    team_list = Team.query.order_by(Team.name).all()
    user = Employee.query.filter_by(id=session['userid']).first()
    username = user.name
    return render_template('employee_manage.html',team_list=team_list,employee_list=employee_list, username=username)


@app.route('/employee',methods=['GET'])
def get_employees():
    employee_id = request.args.get('id')
    if employee_id is not None:
        employee_objs = Employee.query.filter_by(id=employee_id).all()
    else:
        team = request.args.get('team')
        if team is not None:
            employee_objs = Employee.query.filter_by(team=team).order_by(Employee.id).all()   
        else:
            employee_objs = Employee.query.order_by(Employee.id).all()


    employee_list = []
    for each_employee in employee_objs:
        assigned_room_list = Assign.query.filter_by(employee_id=each_employee.id).with_entities(Assign.room_num).all()
        employee_json = {}
        employee_json['assigned_room_list'] = assigned_room_list
        if len(assigned_room_list) == 0:
            employee_json['is_assigned'] = 'unassigned'
        else:
            employee_json['is_assigned'] = 'assigned'
        employee_json['id'] = each_employee.id
        employee_json['name'] = each_employee.name
        employee_json['birthday'] = each_employee.birthday
        employee_json['team'] = each_employee.team
        employee_json['gender'] = each_employee.gender
        employee_json['position'] = each_employee.position
        employee_json['register_timestamp'] = each_employee.register_timestamp
        employee_list.append(employee_json);
    return jsonify({'result':employee_list})


@app.route('/employee/update')
def update_employee():
    employee_json = request.get_json()['employee']
    employee = Employee.query.filter_by(id=employee_json['id']).first()
    if 'name' in employee_json:
        employee.name = employee_json['name']
    if 'team' in employee_json:
        employee.team = employee_json['team']
    try:
        db.session.commit()
    except Exception as e:
        print e
        return jsonify({'result':'db_error','msg':e})
    return jsonify({'result':'success'})


@app.route('/employee/delete',methods=['POST'])
def delete_employee():
    employee_json = request.get_json()['employee']
    try:
        employee = Employee.query.filter_by(id=employee_json['id']).delete()
        db.session.commit()
    except Exception as e:
        print e
        return jsonify({'result':'db_error','msg':e})
    return jsonify({'result':'success'})

@app.route('/employee/add',methods=['POST'])
def add_employee():
    id = request.form['id']
    name = request.form['name']
    password =  request.form['password']
    gender = request.form['gender']
    year = request.form['year']
    month = request.form['month']
    day = request.form['day']
    birthday =  year + month + day
    team =  request.form['team']
    
    if id is None or password is None:
        print 'fill the form'
        return redirect(url_for('signup_page'))

    if Employee.query.filter_by(id=id).first() is not None:
        print 'id already exist'
        return redirect(url_for('signup_page'))

    employee = Employee(id=id, name=name, password=password, team=team, birthday=birthday, gender=gender)
    db.session.add(employee)
    db.session.commit()
    session['userid'] = employee.id
    # user_hash = hashlib.sha1(str(user.id)).hexdigest()
    # session['token'] = user_hash
    return redirect(url_for('main'))


@app.route('/assign', methods=['POST','GET'])
def assign():
    if request.method=='GET':
        assign_list = Assign.query.order_by(Assign.room_num).all()
        return render_template('assign.html',assign_list=assign_list)
    else:    
        employee_id = request.get_json()['employee_id']
        room_list = request.get_json()['room_list']
        
        for each_room_num in room_list:
            assign = Assign(employee_id=employee_id,room_num=int(each_room_num))
            try:
                db.session.add(assign)
                db.session.commit()
                db.session.flush()

                clean = Clean(assign_id=assign.id,check=False)
                db.session.add(clean)
                db.session.commit()
                db.session.flush()
                
                update_room_state(int(each_room_num))

            except Exception as e:
                print e
                return jsonify({'result':'db_error','msg':e})

        return jsonify({'result':'success'})


@app.route('/cleans', methods=['POST'])
def api_clean():
    assign_id = request.json.get('assign_id')
    check = request.json.get('check')
    clean = Clean.query.filter_by(assign_id=int(assign_id)).order_by(desc(Clean.register_timestamp)).first()
    clean.check = bool(check)
    db.session.commit()

    update_room_state(int(Assign.query.filter_by(id=int(assign_id)).first().room_num))
    return jsonify({'result':'success'})

@app.route('/inspect', methods=['POST','GET'])
def inspect():
    if request.method=='GET':
        inspect_list = Inspect.query.order_by(Inspect.room_num).all()
        return render_template('inspect.html',inspect_list=inspect_list)
    else:    
        employee_id = request.get_json()['employee_id']
        room_list = request.get_json()['room_list']
        
        for each_room_num in room_list:
            inspect = Inspect(employee_id=employee_id,room_num=int(each_room_num))
            print 'assign room number',int(each_room_num)
            try:
                db.session.add(inspect)
                db.session.commit()
                db.session.flush()
            except Exception as e:
                print e
                return jsonify({'result':'db_error','msg':e})
        return jsonify({'result':'success'})



@app.route('/room/<room_num>')
def get_room(room_num):
    room = Room.query.filter_by(number=int(room_num)).first()
    room_json = {}
    room_json['number'] = room.number
    print 'get room',room.number
    assign = db.session.query(Employee).join(Assign).filter(Assign.room_num==int(room_json['number'])).order_by(desc(Assign.register_timestamp)).first()
    inspect = db.session.query(Employee).join(Inspect).filter(Inspect.room_num==int(room_json['number'])).order_by(desc(Inspect.register_timestamp)).first()

    reserve = Reserve.query.filter_by(room_num=int(room.number)).order_by(desc(Reserve.register_timestamp)).first()

    if assign is None:
        room_json['assign_employee_id'] = ''
        room_json['assign_class'] = 'assigned_room_overlay'
    else:    
        room_json['assign_employee_id'] = assign.id
        room_json['assign_employee_name'] = assign.name


    if inspect is None:
        room_json['inspect_employee_id'] = ''
        room_json['inspect_class'] = 'inspected_room_overlay'
    else:    
        room_json['inspect_employee_id'] = inspect.id
        room_json['inspect_employee_name'] = inspect.name

    if reserve is None:
        room_json['is_reserved'] = False
        room_json['arrival_date'] = ''
        room_json['departure_date'] = ''
        room_json['is_checkin'] = False
        room_json['is_checkout'] =False
        room_json['customer_name'] =''
        room_json['checkin_time'] = ''
        room_json['checkout_time'] = ''
    else:
        room_json['is_reserved'] = True
        room_json['arrival_date'] = reserve.arrival_date.strftime('%d/%m/%Y')
        room_json['departure_date'] = reserve.departure_date.strftime('%d/%m/%Y')
        room_json['notice'] = reserve.notice
        checkin_time = reserve.checkin_time
        checkout_time = reserve.checkout_time
        print 'checkout',checkout_time
        room_json['is_checkin'] = (checkin_time != None)
        room_json['is_checkout'] = (checkout_time != None)
        room_json['customer_name'] =reserve.customer_name
        if checkin_time is not None:
            room_json['checkin_time'] = checkin_time.strftime('%H:%M')
        else:
            room_json['checkin_time'] = checkin_time

        if checkout_time is not None:
            room_json['checkout_time'] = checkout_time.strftime('%H:%M')
        else:
            room_json['checkout_time'] = checkout_time

    room_json['state'] = room.state
    room_json['register_timestamp'] = room.register_timestamp
    room_json['room_type'] = room.room_type
    return jsonify({'result':room_json})


def update_room_state(room_num):

    
    assign = Assign.query.filter_by(room_num=room_num).order_by(desc(Assign.register_timestamp)).first()
    
    room = Room.query.filter_by(number=room_num).first()
    reserve = Reserve.query.filter_by(room_num=room_num).order_by(desc(Reserve.register_timestamp)).first() #should be applied datetime
    if assign is None:
        if reserve is not None:
            room.state = 'OD'
        else:
            room.state = 'VD'

    else:
        clean = Clean.query.filter_by(assign_id=assign.id).order_by(desc(Clean.register_timestamp)).first()
        
        if reserve is not None:
            if clean.check == False:
                room.state = 'VD'
            else:
                room.state = 'VC'
        else:
            if clean.check == False:
                room.state = 'OD'
            else:
                room.state = 'OC'
    db.session.commit()
    return room.state


@app.route('/add_room',methods=['POST'])
def add_room():
    room_list = request.get_json()['room_list']
    state = 'VC'
    room_type = 'standard'
    notice = ''

    for each_room in room_list:
        #multi input
        try:
            if not RepresentsInt(each_room):
                room_from = re.match('(.*)(-)(.*)',each_room).group(1)
                room_to = re.match('(.*)(-)(.*)',each_room).group(3)
                if int(room_from) > int(room_to):
                    return jsonify({'result':'input_error','msg':'input error'})
                
                for each_room in range(int(room_from), int(room_to)+1):
                    
                    room = Room(number=int(each_room),room_type=room_type,state=state)
                    try:
                        db.session.add(room)
                        db.session.commit()
                        db.session.flush()
                    except Exception as e:
                        print e
                        return jsonify({'result':'db_error','msg':e})
            #single input
            else:
                room = Room(number=int(each_room),room_type=room_type,state=state)
                try:
                    db.session.add(room)
                    db.session.commit()
                    db.session.flush()
                except Exception as e:
                    print e
                    return jsonify({'result':'db_error','msg':e})
        except Exception as e:
            print e
            return jsonify({'result':'input_error','msg':e})
    return jsonify({'result':'success'})


@app.route('/edit_room',methods=['POST'])
def edit_room():
    room_json = request.get_json()['room']
    room = Room.query.filter_by(number=int(room_json['number'])).first()
    
    if 'notice' in room:
        room.notice = room['notice']
    try:
        db.session.commit()
    except Exception as e:
        print e
        return jsonify({'result':'db_error','msg':e})

    update_room_state(room.number)
    return jsonify({'result':'success'})


@app.route('/delete_room',methods=['POST'])
def delete_room():
    room_num = request.get_json()['room']
    try:
        room = Room.query.filter_by(number=int(room_num)).delete()
        db.session.commit()
    except Exception as e:
        print e
        return jsonify({'result':'db_error','msg':e})
    return jsonify({'result':'success'})



@app.route('/checkinout', methods=['POST'])
def checkinout():
    checkinout = request.get_json()['checkinout']
    if 'room_num' in checkinout:
        room_num = checkinout['room_num']
    reserve = Reserve.query.filter_by(room_num=int(room_num)).first()
    customer_name = None
    date_arr = None
    date_dep = None
    time_arr = None
    time_dep = None
    notice = None
    is_vip = None
    checkin_time = None
    checkout_time = None
    '''if reserve is not None:
        customer = reserve.customer_name
        date_arr = reserve.arrival_date
        date_dep = reserve.departure_date
        time_arr = reserve.checkin_time
        notice = reserve.notice
        is_vip = reserve.is_vip
        room_num = reserve.room_num'''

    if '' != checkinout['customer_name']:
        customer_name = checkinout['customer_name']

    if '' != checkinout['date_arr']:
        date_group = re.match('(.*)/(.*)/(.*)',checkinout['date_arr'])
        date_arr = date(int(date_group.group(3)), int(date_group.group(2)), int(date_group.group(1)))

    if '' != checkinout['date_dep']:
        date_group = re.match('(.*)/(.*)/(.*)',checkinout['date_dep'])
        date_dep = date(int(date_group.group(3)), int(date_group.group(2)), int(date_group.group(1)))
        print date_dep
    print checkinout['time_arr']
    if '' != checkinout['time_arr']:
        time_group = re.match('(.*):(.*)',checkinout['time_arr'])
        print int(time_group.group(1))
        print int(time_group.group(2))
        time_arr = time(int(time_group.group(1)), int(time_group.group(2)))

    print 'time departure',checkinout['time_dep']
    if '' != checkinout['time_dep']:
        time_group = re.match('(.*):(.*)',checkinout['time_dep'])
        time_dep = time(int(time_group.group(1)), int(time_group.group(2)))

    if '' != checkinout['notice']:
        notice = checkinout['notice']
    
    reserve = Reserve(room_num=int(room_num), is_vip=is_vip, customer_name=customer_name, arrival_date=date_arr,departure_date=date_dep, checkin_time=time_arr, checkout_time=time_dep,notice=notice)
    db.session.add(reserve)
    db.session.commit()
    db.session.flush()

    update_room_state(int(room_num))
    return jsonify({'result':'success'})




@app.route('/teams')
def get_teams():
    team_list = Team.query.order_by(Team.name).all()
    team_list_json = []
    for each_team in team_list:
        team_list_json.append(each_team.name)
    return jsonify({'team_list':team_list_json})

@app.route('/add_team', methods=['POST'])
def add_team():
    team_name = request.get_json()['team']
    team = Team.query.filter_by(name=team_name).first()
    if team is not None:
        return jsonify({'result':'already exist'}),400
    team = Team(name = team_name)
    db.session.add(team)
    db.session.commit()
    return jsonify({'result':'success'})


@app.route('/edit_team_name', methods=['POST'])
def edit_team_name():
    name_from = request.get_json()['name_from']
    name_to = request.get_json()['name_to']
    team = Team.query.filter_by(name=name_from).first()
    if team is None:
        return jsonify({'result':'not exist'}),400
    team.name = name_to
    db.session.commit()
    return jsonify({'result':'success'})



@app.route('/delete_team', methods=['POST'])
def delete_team():
    team_name = request.get_json()['team']
    team = Team.query.filter_by(name=team_name).first()
    if team is None:
        return jsonify({'result':'team not exist'}),400
    db.session.delete(team)
    db.session.commit()
    return jsonify({'result':'success'})



@app.route('/add_staff', methods=['POST'])
def add_staff():
    staff = request.get_json()['staff']
    #current_time = datetime.datetime.now().strftime("%Y-%m-%d,%H:%M:%S")
    #hash = hashlib.md5(staff['name']+current_time).hexdigest()

    exist_employee = Employee.query.filter_by(id=staff['name']).all()
    if len(exist_employee) != 0:
        id = staff['name']+str(len(exist_employee)+1)
    else:
        id = staff['name']
    name = staff['name']
    password =  staff['name']
    gender = None
    year = ''
    month = ''
    day = ''
    birthday =  year + month + day
    position =  staff['position']
    team = None

    if id is None or password is None:
        print 'fill the form'
        return redirect(url_for('signup_page'))

    if Employee.query.filter_by(id=id).first() is not None:
        print 'id already exist'
        return redirect(url_for('signup_page'))

    employee = Employee(id=id, name=name, password=password, position=position, birthday=birthday, gender=gender)
    db.session.add(employee)
    db.session.commit()
    return jsonify({'result':'success'})

@app.route('/delete_staff', methods=['POST'])
def delete_staff():
    staff_id = request.get_json()['staff']
    employee = Employee.query.filter_by(id=staff_id).first()
    if employee is None:
        return jsonify({'result':'team not exist'}),400
    db.session.delete(employee)
    db.session.commit()
    return jsonify({'result':'success'})

@app.route('/edit_staff', methods=['POST'])
def edit_staff():
    staff_id = request.get_json()['staff_id']
    name_to = request.get_json()['name_to']
    staff_position = request.get_json()['staff_position']
    staff_team = request.get_json()['staff_team']
    staff = Employee.query.filter_by(id=staff_id).first()
    if staff is None:
        return jsonify({'result':'not exist'}),400
    staff.name = name_to
    staff.position = staff_position
    staff.team = staff_team
    db.session.commit()
    return jsonify({'result':'success'})





@app.route('/logout')
def logout():
    # remove the user from the session if it's there
    logout_user()
    session['userid'] = None
    return redirect(url_for('login'))


def filter_get_user_list(each_employee, request):
    query_user_name = request.args.get('name')
    query_user_team = request.args.get('team')
    query_user_room_num = request.args.get('room_num')
    query_user_position = request.args.get('position')

    if query_user_name is not None:
        if not query_user_name == each_employee.name:
            return False
    if query_user_team is not None:
        if not query_user_team == each_employee.team:
            return False
    if query_user_position is not None:
        if not query_user_position == each_employee.position:
            return False
    if query_user_room_num is not None:
        assigned = db.session.query(Assign).filter(and_(
            Assign.employee_id == each_employee.id,
            Assign.room_num == int(query_uuer_room_num))).first()
        if assigned is None:
            return False
    return True

#mobile api
@app.route('/users')
def get_user_list():
    employee_list = [each_employee.serialize for each_employee in Employee.query.order_by(Employee.id).all() if filter_get_user_list(each_employee,request) ]
    return jsonify({'result':employee_list})

@app.route('/users/login', methods=['POST'])
def api_login():
    if request.method=='POST':
        login_id = request.json.get('id')
        login_pw = request.json.get('pw')

        employee = Employee.query.filter_by(id=login_id).first()
        employee.recent_login_timestamp = datetime.now()
        db.session.commit()

        try:
            if not employee.verify_password(login_pw):
                raise ValueError('Could not find correct user!')
        except:
            return jsonify({'message':'id or pw is invalide'}),400

        token = employee.generate_auth_token()

        print ptime.time()
        now = int(ptime.time())
        expires = now + (app.config['ONLINE_LAST_MINUTES'] * 60) + 10
        p = redis.pipeline()

        if redis.get(token) is None:
            p.set(token,{'id':employee.id, 'time':int(ptime.time())})
        p.expireat(token, expires)
        p.execute()

        print 'redis', ast.literal_eval(redis.get(token))['id']
        #redis.flushdb() 

        return jsonify({'result':{'token':token,'name':employee.name,'team':employee.team,'position':employee.position }})


@app.route('/users/logout', methods=['GET'])
@token_required
def api_logout():
    token = request.headers.get('Authorization')
    if token is None:
        return jsonify({'error','no token headers'})
    token = token[6:]
    if redis.get(token) is not None:
        redis.delete(token)
    else:
        return jsonify('error','token invalid')

    return jsonify({'result':'success'})


@app.route('/users/me')
@token_required
def api_about_me():
    my_info = Employee.query.filter_by(id=session['userid']).first()
    db.session.commit()
    print redis.keys()
    if my_info is None:
        return jsonify({'message':'login first'}),400
    return jsonify({'result':my_info.serialize})



@app.route('/rooms', methods=['GET'])
def api_get_rooms():
    state = request.args.get('state')
    room_num = request.args.get('room_num')
    cleaner_id = request.args.get('cleaner_id') 
    supervisor_id = request.args.get('supervisor_id')

    if len(request.args) != 0:

        room_query = []

        if room_num is not None:
            room_query.append(db.session.query(Room).filter(Room.number==room_num))
        if state is not None:
            room_query.append(Room.state.contains(state))
        if cleaner_id is not None:
            room_query.append(Assign.employee_id.contains(cleaner_id))
        if supervisor_id is not None:
            room_query.append(Inspect.employee_id.contains(supervisor_id))

        room_list = db.session.query(Room).outerjoin(Reserve).outerjoin(Assign).outerjoin(Inspect).filter(and_(
                    *room_query)).order_by(Room.number).all()
    else:
        room_list = Room.query.order_by(Room.number).all()

    room_json_list = []
    for each_room in room_list:
        room_json = {}
        room_json['room_number'] = each_room.number
        room_json['room_type'] = each_room.room_type
        room_json['state'] = each_room.state
        if each_room.assign.first() is not None:
            room_json['cleaner_id'] = each_room.assign.first().employee_id
        if each_room.assign.first() is not None:
            room_json['assign_id'] = each_room.assign.first().id
        if each_room.assign.first() is not None:
            room_json['clean_assigned_datetime'] = each_room.assign.first().register_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        if each_room.inspect.first() is not None:
            room_json['evaluator_id'] = each_room.inspect.first().employee_id
        if each_room.assign.first() is not None:
            room_json['inspect_assigned_datetime'] = each_room.assign.first().register_timestamp.strftime("%Y-%m-%d %H:%M:%S")

        if each_room.reserve.first() is not None: 
            if each_room.reserve.first().notice is not None:
                room_json['notice'] = each_room.reserve.first().notice

        if each_room.reserve.first() is not None: 
            if each_room.reserve.first().checkin_time is not None:
                room_json['checkin_time'] = each_room.reserve.first().arrival_date.strftime("%Y-%m-%d ")+each_room.reserve.first().checkin_time.strftime("%H:%M:%S")
                print room_json['checkin_time']

        if each_room.reserve.first() is not None: 
            if each_room.reserve.first().checkout_time is not None:
                room_json['checkout_time'] = each_room.reserve.first().departure_date.strftime("%Y-%m-%d ")+each_room.reserve.first().checkout_time.strftime("%H:%M:%S")

        if each_room.reserve.first() is not None: 
            if each_room.reserve.first().arrival_date is not None:
                room_json['arrival_date'] = each_room.reserve.first().arrival_date.strftime("%Y-%m-%d %H:%M:%S")

        if each_room.reserve.first() is not None: 
            if each_room.reserve.first().departure_date is not None:
                room_json['departure_date'] = each_room.reserve.first().departure_date.strftime("%Y-%m-%d %H:%M:%S")
        room_json_list.append(room_json)
    return jsonify({'result':room_json_list})

@app.route('/evaluation',methods=['GET','POST'])
def api_evaluation(**kwargs):
    if request.method == 'GET':
        cleaner_id = request.args.get('cleaner_id')
        evaluator_id = request.args.get('evaluator_id')
        description = request.args.get('description')
        evaluation_query = []
        if cleaner_id is not None:
            evaluation_query.append(db.session.query(Assign).filter(Assign.employee_id==cleaner_id))
        if evaluator_id is not None:
            evaluation_query.append(db.session.query(Inspect).filter(Inspect.employee_id==evaluator_id))
        if description is not None:
            evaluation_query.append(db.session.query(Inspection_form).filter(Inspection_form.contains(description)))

        evaluation_list = db.session.query(Evaluation).join(Assign).join(Inspect).filter(and_(
            *evaluation_query)).order_by(Evaluation.id).all()

        evaluation_json_list = []
        for each_evaluation in evaluation_list:
            evaluation_json = {}
            evaluation_json['id'] = each_evaluation.id
            evaluation_json['timestamp'] = each_evaluation.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            evaluation_json['point'] = each_evaluation.check
            inspection_form = Inspection_form.query.filter_by(id=each_evaluation.inspection_form_id).first()

            evaluation_json['description'] = inspection_form.description
            evaluation_json['total_point'] = inspection_form.total_point

            if each_room.assign.first() is not None:
                room_json['cleaner_id'] = each_room.assign.first().employee_id
            if each_room.assign.first() is not None:
                room_json['room_num'] = each_room.assign.first().room_num
            if each_room.inspect.first() is not None:
                room_json['evaluator_id'] = each_room.inspect.first().employee_id
            
            evaluation_json_list.append(evaluation_json)

        return jsonify({'result':evaluation_json_list})
    else:
        room_num = int(request.json.get("room_num"))
        evaluation_type = request.json.get("type")
        evaluation_form_dict = request.json.get("evaluation_form_dict")
        for form_id, check in evaluation_form_dict.iteritems():
            assign_id = Assign.query.filter_by(room_num=room_num).first().id
            inspect_id = Inspect.query.filter_by(room_num=room_num).first().id
            evaluation = Evaluation(check=check, inspection_form_id=form_id, assign_id=assign_id, inspect_id=inspect_id)
            db.session.add(evaluation)
        db.session.commit()
        return jsonify({'result':{'total_point':'0'}})#will be implement later



@app.route('/')
@app.route('/login' , methods=['GET', 'POST'])
def login():
    if request.method=='GET':
        try:
            if 'request_url' in request.args:
                session['request_url'] = request.args['request_url']
        except Exception as e:
            print e
        if session.get('userid') is not None:
            return redirect(url_for('main'))
        # if g.get('user', None) is not None:
        #     return redirect(url_for('main'))
    	return render_template("login.html")

    else:

        userid = request.form['id']
        password = request.form['password']
        employee = Employee.query.filter_by(id=userid).first()

        try:
            if not employee.verify_password(password):
				error_msg = "아이디와 비밀번호를 확인해주세요"
				flash(error_msg)
				return render_template("login.html", error_msg=error_msg)
        except:
			error_msg = "아이디와 비밀번호를 확인해주세요"
			flash(error_msg)
			return render_template("login.html", error_msg=error_msg)

        user_hash = hashlib.sha1(str(employee.id)).hexdigest()
        session['userid'] = employee.id
        # username = re.match('(.*)(@)',user.email).group(1)
        
        if 'request_url' in session:
            return redirect(session['request_url'])
        return redirect(url_for('main'))



@app.route('/main', methods=['POST','GET'])
@login_required
def main():
    if request.method=='GET':
        if not 'userid' in session:
            return redirect(url_for('login'))
        user = Employee.query.filter_by(id=session['userid']).first()
        if user is None:
            logout()

        username = user.name
        

        search_query = request.args.get('search')
        if (search_query is not None ) and (search_query != ''):
            room_list = db.session.query(Room).join(Reserve).filter(or_(
                Room.number.contains(int(search_query)),
                Room.state.contains(search_query),
                Room.room_type.contains(search_query),
                Reserve.customer_name.contains(search_query),
                Reserve.customer_name.contains(search_query))).order_by(Room.number).all()
            
        else:
            search_query = ''
            room_list = Room.query.order_by(Room.number).all()



        room_floor_list = {}
        for each_room in room_list:

            room_json = json.loads(get_room(each_room.number).data)['result']
            
            if not str(each_room.number/100) in room_floor_list:
                room_floor_list[str(each_room.number/100)]= {'room_list':[]}
                room_floor_list[str(each_room.number/100)]['room_list'].append(room_json)
            else:
                room_floor_list[str(each_room.number/100)]['room_list'].append(room_json)
        
        for floor,each_floor in room_floor_list.iteritems():
            room_floor_list[floor]['floor_room_len'] = len(each_floor['room_list'])

        
        return render_template("main.html",username=username,room_floor_list=room_floor_list) #search_query=search_query,username=username,user_q=user.q_point, profile_picture=user.profile_picture,survey_list=survey_list)





@app.route('/inspection')
def inspection_page():
    user = Employee.query.filter_by(id=session['userid']).first()
    username = user.name
    return redirect(url_for('form_data_page'))
    #return render_template('not_inspected_room.html',username=username)

@app.route('/assign_inspection')
def assign_inspection():
    user = Employee.query.filter_by(id=session['userid']).first()
    username = user.name
    return render_template('not_inspected_room.html',username=username)

@app.route('/inspection_analysis')
@app.route('/inspection/form_data')
def form_data_page():
    user = Employee.query.filter_by(id=session['userid']).first()
    username = user.name
    form_list = json.loads(get_form().data)['result']


    for i in range(len(form_list)):
        each_form = form_list[i]
        evaluation = Evaluation.query.filter_by(inspection_form_id=each_form['id']).all()

        form_list[i]['evaluation_list'] = db.session.query(Evaluation).join(Assign).join(Inspect).filter(
            Evaluation.inspection_form_id==each_form['id']).order_by(Assign.room_num.asc(),Evaluation.timestamp.desc()).all()

    return render_template('inspection_analysis_form_data.html',username=username,form_list=form_list)



@app.route('/not_inspected_room')
def not_inspected_room():
    user = Employee.query.filter_by(id=session['userid']).first()
    username = user.name
    return render_template('not_inspected_room.html',username=username)

@app.route('/not_inspected_cleaner')
def not_inspected_cleaner():
    user = Employee.query.filter_by(id=session['userid']).first()
    username = user.name
    return render_template('not_inspected_cleaner.html',username=username)


@app.route('/form', methods=['POST'])
def add_form():
    form_type = request.json.get('form_type')
    form_num = request.json.get('form_num') 
    form_description = request.json.get('form_description')
    form_total_point = request.json.get('form_total_point')
    form_id = request.json.get('form_id')

    if form_id is not None:
        inspection_form = Inspection_form.query.filter_by(id=int(form_id)).first()
        inspection_form.form_type = form_type
        inspection_form.form_num = int(form_num)
        inspection_form.form_description = form_description
        inspection_form.form_total_point = int(form_total_point)
    else:
        inspection_form = Inspection_form(form_type=form_type, form_num=form_num, description=form_description, total_point=form_total_point)
        db.session.add(inspection_form)

    db.session.commit()
    return jsonify({'result':'success'})


@app.route('/form', methods=['GET'])
@app.route('/form/<form_id>', methods=['GET'])
def get_form(**kwargs):
    form_id = kwargs.get('form_id')
    form_type = request.args.get('form_type')
    form_num =  request.args.get('form_num')
    form_description =  request.args.get('description')
    form_total_point =  request.args.get('total_point')

    if form_id is not None:
        inspection_form_list = Inspection_form.query.filter_by(id=form_id).all()
    else:
        inspection_form_list = Inspection_form.query.order_by(Inspection_form.form_type.desc(), Inspection_form.form_num.asc()).all()
    
    inspection_form_json_list = []
    for each_inspection_form in inspection_form_list:
        if form_type is not None:
            if form_type != each_inspection_form.form_type:
                continue
        if form_num is not None:
            if int(form_num) != each_inspection_form.form_num:
                continue
        if form_description is not None:
            if form_description != each_inspection_form.description:
                continue
        if form_total_point is not None:
            if int(form_total_point) != each_inspection_form.total_point:
                continue

        inspection_form_json = {}
        inspection_form_json['id'] = int(each_inspection_form.id)
        inspection_form_json['form_type'] = each_inspection_form.form_type
        inspection_form_json['form_num'] = int(each_inspection_form.form_num)
        inspection_form_json['description'] = each_inspection_form.description
        inspection_form_json['total_point'] = int(each_inspection_form.total_point)
        inspection_form_json_list.append(inspection_form_json)

    return jsonify({'result':inspection_form_json_list})




@app.route('/walkie/channel/<channel_id>')
@app.route('/walkie/channel')
def walkie_channel(**kwargs):
    walkie_channel_id = kwargs.get('channel_id')
    if walkie_channel_id is not None:
        walkie_channel = Walkie_channel.query.filter_by(id=walkie_channel_id).all()
    else:
        walkie_query = []
        walkie_channel_member = request.args.get('joined_member')
        walkie_channel_name = request.args.get('channel_name')
        print walkie_query
        if walkie_channel_name is not None:
            walkie_query.append(db.session.query(Walkie_channel).filter(Walkie_channel.contains(walkie_channel_name)))
        if walkie_channel_member is not None:
            walkie_query.append(db.session.query(Walkie_member).filter(Walkie_member.id==walkie_channel_id))

        walkie_channel_list = db.session.query(Walkie_channel).join(Walkie_member).filter(and_(
            *walkie_query)).order_by(Walkie_channel.id).all()

    return jsonify({'result':[{'channel_id': each_channel.id,
        'channel_name':each_channel.name,
        'member_list': [each_channel.id for each_member in Walkie_member.query.filter_by(channel_id=each_channel.id)],
        'host_id':each_channel.host_id} for each_channel in walkie_channel_list]})


@app.route('/walkie/channel',methods=['POST'])
#@token_required
def make_channel():
    print request.data
    channel_name = request.json.get('channel_name')
    members_list = request.json.get('member_list')
    members_list.append(session['userid'])
    walkie_channel = Walkie_channel(channel_name=channel_name, host_id=session['userid']).first()
    db.session.add(walkie_channel)
    db.session.commit()
    db.session.flush()
    for each_member in members_list:
        walkie_member = Walkie_member(channel_id=walkie_channel.id, member_id=each_member.id)
        db.session.add(walkie_member)
    db.session.commit()
    db.session.flush()
    return jsonify({'result':{'channel_id':walkie_channel.id,
        'channel_name':walkie_channel.channel_name,
        'member_list':members_list,
        'host_id':session['userid']}})


def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
