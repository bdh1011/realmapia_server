from bs4 import BeautifulSoup
import unittest
from app import create_app, db, bcrypt
import json
from flask import Flask, Blueprint, request


class APITestCase(unittest.TestCase):
    """ setup and teardown for testing the database """
    def setUp(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()


    def test_api_user(self):
    	rv = self.client.get('api/users',
    		headers={'Authorization':'Basic 1'},follow_redirects=True)
    	assert 'result' in rv.data
    	print json.loads(rv.data)['result']

    def test_api_login(self):
    	rv = self.client.post('api/users/login',
    		data=dict(id='admin',pw='1'),
    		headers={'content-type':'application/json'},follow_redirects=True)
    	print rv.data
    	assert 'result' in rv.data

    	print json.loads(rv.data)['result']

    def test_api_get_users_options(self):
    	rv = self.client.post('api/users/login?name=admin',
    		data=dict(id='admin',pw='1'),
    		headers={'Authorization':'Basic 1','content-type':'application/json'},follow_redirects=True)
    	print rv.data
    	assert 'result' in rv.data
    	print json.loads(rv.data)['result']

    def test_api_users_me(self):
    	rv = self.client.get('api/users/me',
    		headers={'Authorization':'Basic 1'},follow_redirects=True)
    	assert 'result' in rv.data
    	print json.loads(rv.data)['result']

    def test_api_get_rooms(self):
    	rv = self.client.get('api/rooms',
    		headers={'Authorization':'Basic 1'},follow_redirects=True)
    	assert 'result' in rv.data
    	print json.loads(rv.data)['result']

    def test_api_get_forms(self):
    	rv = self.client.get('api/form',
    		headers={'Authorization':'Basic 1'},follow_redirects=True)
    	assert 'result' in rv.data
    	print json.loads(rv.data)['result']


    def test_api_get_form(self):
    	rv = self.client.get('api/form/1',
    		headers={'Authorization':'Basic 1'},follow_redirects=True)
    	assert 'result' in rv.data
    	print '-------form--------'
    	print json.loads(rv.data)['result']


    def test_api_evaluate(self):
    	
    	rv = self.client.post('api/evaluation',
    		data=json.dumps({
    		'room_num':101,
    		'type':'short',
    		'inspection_form_dict':{1:{'check':True,'comment':'hi'}}
    		}),
    		headers={'Authorization':'Basic 1'},
    		content_type='application/json')
    	print '----evaluate------'
    	print rv.data
    	assert 'result' in rv.data
    	print json.loads(rv.data)['result']


    def test_api_get_evaluation(self):
    	rv = self.client.get('api/evaluation',
    		headers={'Authorization':'Basic 1'},follow_redirects=True)
    	print '-------evaluation--------'
    	assert 'result' in rv.data
    	print json.loads(rv.data)['result']


    def test_api_clean(self):
    	
    	rv = self.client.post('api/cleans',
    		data=json.dumps({
    		'room_num':101,
    		'state':'VC',
    		}),
    		headers={'Authorization':'Basic 1'},
    		content_type='application/json')


    	print '-------clean--------'
    	print rv.data
    	assert 'result' in rv.data
    	print json.loads(rv.data)['result']



    def test_api_get_requirement(self):
    	rv = self.client.get('api/requirements/101',
    		headers={'Authorization':'Basic 1'},follow_redirects=True)
    	assert 'result' in rv.data
    	print '-------requirements--------'
    	print json.loads(rv.data)['result']



    def test_api_post_requirement(self):
    	rv = self.client.post('api/requirements/101',
    		data=json.dumps({
	    		'requirement':'hihi'
    		}),
    		headers={'Authorization':'Basic 1'},
    		content_type='application/json')

    	print rv.data
    	assert 'result' in rv.data
    	print '-------post requirements--------'
    	print json.loads(rv.data)['result']



    def test_api_get_channel(self):
    	rv = self.client.get('api/walkie/channel',
    		headers={'Authorization':'Basic 1'},follow_redirects=True)
    	assert 'result' in rv.data
    	print '-------channel--------'
    	print json.loads(rv.data)['result']




    def test_api_post_channel(self):
    	rv = self.client.post('api/walkie/channel',
    		data=json.dumps({
	    		'channel_name':'hihi',
	    		'member_list':['admin']
    		}),
    		headers={'Authorization':'Basic 1'},
    		content_type='application/json')

    	print rv.data
    	assert 'result' in rv.data
    	print '-------make channel--------'
    	print json.loads(rv.data)['result']



    def test_api_delete_channel(self):
    	rv = self.client.delete('api/walkie/channel/1',
    		headers={'Authorization':'Basic 1'},
    		content_type='application/json')

    	print rv.data
    	assert 'result' in rv.data
    	print '-------delete channel--------'
    	print json.loads(rv.data)['result']



    def test_api_exit_channel(self):
    	rv = self.client.get('api/walkie/channel/1/member/exit',
    		headers={'Authorization':'Basic 1'},
    		content_type='application/json')

    	print rv.data
    	assert 'result' in rv.data
    	print '-------exit channel--------'
    	print json.loads(rv.data)['result']



    # def test_api_login(self):
    #     res = self.client.post('/api/users/', data=dict(
    #         id='admin',
    #         pw='1'
    #     ), follow_redirects=True)

    #     soup = BeautifulSoup(res.data)
    #     assert soup

    # def test_login_fail(self):
    #     res = self.login('randomuser', 'randompass')
    #     soup = BeautifulSoup(res.data)
    #     d = soup.find('span', 'flashdata')
    #     assert d.text == u'No such user. Please try again'

    # def test_login_success(self):
    #     res = self.login('admin', '1')
    #     soup = BeautifulSoup(res.data)
    #     d = soup.find('span', 'flashdata')
    #     assert d.text == u'Logged in successfully'

    # def test_logout(self):
    #     res = self.client.get('/users/logout/', follow_redirects=True)
    #     soup = BeautifulSoup(res.data)
    #     d = soup.find('span', 'flashdata')
    #     assert d.text == u'User logged out'

