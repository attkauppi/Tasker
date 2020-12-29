""" Tasker API resources """

from flask import Flask, jsonify, abort, make_response, g, request
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask_httpauth import HTTPBasicAuth
from application.models import User, Task
from application.api.errors import forbidden#, unauthorized
from application.api import api_bp_restful
from application import db

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username_or_token, password):
    """ Basic auth checking for users. Allows use of
    either a token or username and password to authenticate 
    
    - if email_or_token field is empty, can't be either
    authentication method
    - if password field is empty, assume token
    - if neither field is empty, assume regular username
    password authentication.
    """
    if username_or_token == '':
        return False
    if password == '':
        g.current_user = User.verify_auth_token(username_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(username=username_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.check_password(password)

@auth.error_handler
def unauthorized():
    """ Returns 403 instead of 401 to prevent
    browsers from displaying the default auth
    dialog """
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)

#@api_bp_restful.before_request
#@auth.login_required
#def before_request():
#    if not g.current_user.is_anonymous and not g.current_user.confirmed:
#        return forbidden('Unconfirmed account')

class AuthAPI(Resource):
    """ Authentication """

    def post(self):
        """ Receives auth """
        if g.current_user.is_anonymous or g.token_used:
            return unauthorized('Invalid credentials')
        return jsonify({'token': g.current_user.generate_auth_token(
            expiration=3600), 'expiration': 3600})

# tasks
tasks = {
    "cards": [
        {
            'description': u'eras tehtava',
            'id': 1,
            'position': u'yellow',
            'priority': False,
            'title': u'tehtavan otsikko'
        },
        {
            'description': u'eras toinen tehtava',
            'id': 2,
            'position': u'green',
            'priority': False,
            'title': u'toisen tehtavan otsikko'
        }
    ],
    "config": {
        'maxid': 2
    }
}


# Template for marshal
task_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'position': fields.String,
    'priority': fields.Boolean
}


class TaskDeleteAPI(Resource):
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=int, required=True,
                                   help='no id provided for task to be deleted',
                                   location='json')
        super(TaskDeleteAPI, self).__init__()


    # def post(self):
    #     data = request.get_json(force=True)
    #     t = Task.query.filter_by(id=data['id']).first()

    #     print("Löytyi tehtävä: ", t)




class TaskListAPI(Resource):
    #decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, required=True,
                                   help='No task title provided',
                                   location='json')
        self.reqparse.add_argument('description', type=str, default="",
                                   location='json')
        super(TaskListAPI, self).__init__()

    def get(self):
        print("Pyyntö")
        tasks = Task.query.all()
        print("Tasks: ", tasks)
        d = {}
        
        
        d['cards'] = []
        d['config'] = {}

        max_id = 0
        for i in tasks:
            if i.id >= 0:
                max_id = i.id
            dc = {
                'description': i.description,
                'id': i.id,
                'position': i.position,
                'priority': False,
                'title': i.title
            } 
                
                
                
            d['cards'].append(dc)
        d['config']['maxid'] = max_id

        print("d lopussa: ", d)

        return jsonify(d)

    def post(self):
        #args = self.reqparse.parse_args()
        print("SAATU PYYNTÖ")
        data = request.get_json(force=True)
        print(data)

        cards = data['cards']
        tasks = Task.query.all()
        d = {}
        d['cards_modified'] = []
        something_changed = False

        card_list = []
        for i in cards:
            tehtava = Task.query.filter_by(id=i['id']).first()
            if tehtava is not None:
                if tehtava.title != i['title']:
                    something_changed = True
                    tehtava.title = i['title']
                if tehtava.description != i['description']:
                    something_changed = True
                    tehtava.description = i['description']
                if tehtava.position != i['position']:
                    something_changed = True
                    tehtava.position = i['position']

                if something_changed:
                    dc = {
                        'description': tehtava.description,
                        'id': tehtava.id,
                        'position': tehtava.position,
                        'priority': False,
                        'title': tehtava.title
                    }
                    d['cards_modified'].append(dc)
                #if tehtava.priority != i['priority']:
                #    tehtava.priority = i['priority']
                db.session.merge(tehtava)
                db.session.commit()
        
        return jsonify(d)
            #    db.session.delete(tehtava)
            #    db.session.commit()
                #return {"msg": "Deleted " + tehtava}
            #else:
            
                
                
                # try:
                #     instance = Task.query.filter_by(id=i['id']).first()
                #     instance.update(dict(data[i]))
                #     db.session.commit()
                #     updateddata=instance.first()
                #     msg={"msg":"Task details updated successfully","data":updateddata.serializers()}
                # except Exception as e:
                #     print(e)
                #     msg = {'msg': "Failed to update something: "}
                #     code=500
                #     return msg
                    
        
                    # if tehtava.title != i['title']:
                    
                    #     tehtava.title = i['title']
                    # if tehtava.description != i['description']:
                    #     tehtava.description = i['description']
                    # if tehtava.position != i['position']:
                    #     tehtava.position = i['position']
                    # #if tehtava.priority != i['priority']:
                    # #    tehtava.priority = i['priority']
                    # db.session.


        


        
        #print("cards: ", cards)
        #return jsonify(data)
        # task = {
        #     'id': tasks[-1]['id'] + 1 if len(tasks) > 0 else 1,
        #     'title': args['title'],
        #     'description': args['description'],
        #     'done': False
        # }
        # tasks.append(task)
        #return {'task': marshal(task, task_fields)}, 201


            #d['cards'].append

        #return {''}
    # def __init__(self):
    #     self.reqparse = reqparse.RequestParser()
    #     self.reqparse.add_argument('id', type=int, location="json")
    #     self.reqparse.add_argument('title', type=str, location='json')
    #     self.reqparse.add_argument('position', type=str, location='json')
    #     self.reqparse.add_argument('description', type=str, location='json')
    #     self.reqparse.add_argument('priority', type=bool, location='json')
    #     super(TaskAPI)
