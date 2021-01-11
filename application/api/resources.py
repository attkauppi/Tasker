""" Tasker API resources """

from flask import Flask, jsonify, abort, make_response, g, request
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask_httpauth import HTTPBasicAuth
from application.models import User, Task
from application.api.errors import forbidden#, unauthorized
from application.api import api_bp_restful
from application import db
from datetime import datetime
from sqlalchemy import func 
import logging
from sqlalchemy import asc
auth = HTTPBasicAuth()

#tasks = set(Task.query.all())
#print(tasks)

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

@api_bp_restful.before_request
@auth.login_required
def before_request():
   if not g.current_user.is_anonymous and not g.current_user.confirmed:
       return forbidden('Unconfirmed account')

class AuthAPI(Resource):
    """ Authentication """

    def post(self):
        """ Receives auth """
        if g.current_user.is_anonymous or g.token_used:
            return unauthorized('Invalid credentials')
        return jsonify({'token': g.current_user.generate_auth_token(
            expiration=3600), 'expiration': 3600})

taskss = [
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
    ]


# Template for marshal
task_fields = {
    'title': fields.String,
    'description': fields.String,
    'position': fields.String,
    'priority': fields.Boolean,
    #'uri': fields.Url()
    #'uri': fields.Url(api_bp.task)
}

class TaskAPI(Resource):

    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        
        self.reqparse.add_argument('title', type=str, required=True,
                                   help='No task title provided',
                                   location='json')
        self.reqparse.add_argument('description', type=str, default="description",
                                   location='json')
        super(TaskAPI, self).__init__()
    
    def get(self, id):
        task = Task.query.filter_by(id=id).first()
        if task is None:
            abort(404)
        return task.to_json()
    
    def put(self, id):
        """ update task """
        r = request.get_json(force=True)
        
        task = Task.query.filter_by(id=id).first()
        if task is None:
            abort(404)
        
        if task.title != r['title']:
            task.title = r['title']
        if task.description != r['description']:
            task.description = r['description']
        if task.position != r['position']:
            task.position = r['position']
        if task.priority != r['priority']:
            task.priority = r['priority']
        # if task.done != r['done']:
        #     task.done = r['done']
        
        db.session.commit()
        
        return task.to_json()
    
    def delete(self, id):

        try:
            Task.query.filter_by(id=id).delete()
            db.session.commit()
        except Exception as e:
            return {"msg": "not found"}

        return {"msg": "deleted"}
    
    def post(self):
        """ API endpoint used to create tasks """
        data = request.get_json(force=True)
        user = g.current_user

        #print("Current_user: ", g.current_user)
        #print("user", user)

        task = Task.query.filter_by(id=data[id]).first()

        User.verify_auth_token()

        if task is not None:
            task.position = data['position']
            task.priority = data['priority']
            db.session.commit()
            return jsonify(
            {
                'id': task.id,
                'title':task.title,
                'description':task.description,
                'priority': task.priority,
                'position': task.position
            })
            

        print("Task apin saama post: ", data)

        t = Task(
            title=data['title'],
            description=data['description'],
            position = data['position'],
            priority=data['priority'],
            created = datetime.utcnow()
            # TODO: lisää kun olet lisännyt teitokantaan kentän
            # priority = data['priority]
        )
        db.session.add(t)
        db.session.commit()

        t = Task.query.filter_by(created=t.created).first()

        return jsonify({
            'id': t.id,
            'title':t.title,
            'description':t.description,
            'priority': t.priority,
            'position': t.position
        })

        #return jsonify({'id': t.id, 'title':t.title, 'description':t.description,})

        #t = Task.query.filter_by(id=data['id']).first()


class TaskCheckAPI(Resource):

    decorators = [auth.login_required]
    
    def __init__(self):
        data = request.get_json()
        #user = User
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=int, required=True,
                                   help='no id provided for task to be deleted',
                                   location='json')
        super(TaskCheckAPI, self).__init__()


    def post(self,id):
        data = request.get_json(force=True)
        #user = g.current_user
        #print("User: ", user)
        #data = request.get_json(force=True)
        t = Task.query.filter_by(id=id).first()
        
        cardMismatch = False

        if t is not None:
            if t.description != data['description']:
                print("Kuvaus erosi")
                cardMismatch = True
            if t.title != data['title']:
                print("Otsikko erosi")
                cardMismatch = True
            if t.position != data['position']:
                print("position erosi")
                cardMismatch = True
            if t.priority != data['priority']:
                print("priority erosi")
                cardMismatch = True
            # if t.done != data['done']:
            #     print("done erosi")
            #     cardMismatch = True

            if not cardMismatch:
                return {"keep": True}
            else:
                return {"keep": False}
        
        return {"keep": False}
        





class TaskListAPI(Resource):

    #decorators = [auth.login_required]
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, required=True,
                                   help='No task title provided',
                                   location='json')
        self.reqparse.add_argument('description', type=str, default="",
                                   location='json')
        super(TaskListAPI, self).__init__()

    def get(self):
        # user = g.current_user
        print(request.headers)
        #print("User: ", user)
        #tasks = Task.query.all().order_by(asc(Task.id))
        tasks = db.session.query(Task).order_by(Task.id)
        print("Tasks: ", tasks)

        #maxid = db.session.query(func.max(Task.id))
        #print("Max id: ", maxid)
        #print("Current_user: ", g.current_user)


        d = {}
        d['cards'] = []
        maxid = 0
        for i in tasks:#Task.query.all():
            #if i.id > maxid:
            #    maxid = i.id
            #print(i)
            print(i.to_json())
            id_luku = i.id
            dt = {
                'description': i.description,
                'id': i.id,
                'position': i.position,
                'priority': i.priority,
                'title': i.title
            }

            d['cards'].append(dt)
            
            #if i.id > maxid:
            if maxid < id_luku:
                maxid = id_luku
        
        d['config'] = {}
        d['config']['maxid'] = maxid

        return d, 201

        #return {'cards': [task.to_json() for task in tasks],
        #    "config": {'maxid': maxid}
        #}
        
        # print("Current_user: ", g.current_user)
        # print("Pyyntö")
        # tasks = Task.query.all()
        # print("Tasks: ", tasks)
        # d = {}
        
        
        # d['cards'] = []
        # d['config'] = {}

        # max_id = 0
        # for i in tasks:
        #     if i.id >= 0:
        #         max_id = i.id
        #     dc = {
        #         'description': i.description,
        #         'id': i.id,
        #         'position': i.position,
        #         'priority': i.priority,
        #         'title': i.title
        #     } 
                
                
                
        #     d['cards'].append(dc)
        # d['config']['maxid'] = max_id

        # print("d lopussa: ", d)

        # return jsonify(d)

    def post(self):
        """ Create a new task """
        r = request.get_json(force=True)
        print("tasklistapin post pyyntö: ", r)
        print("request: ", request.get_json(force=True))
        #print("Current_user: ", g.current_user)
        args = self.reqparse.parse_args()
        print("post pyynnön argit: ", args)

        task = Task(
            title=args['title'],
            description = args['description']
            #position = args['position'],
            #priority = args['priority']
        )

        task.position = r['position']
        task.priority = r['priority']
        #task.done = r['done']
        task.done = False
        task.creator_id = g.current_user.id



        db.session.add(task)
        db.session.commit()

        t = Task.query.filter_by(title=task.title).filter_by(creator_id=g.current_user.id).first()
        print("Tehtävä id: ", t.id)

        return t.to_json()

        #return {'task': marshal(task, task_fields)}, 201

        
        



        #args = self.reqparse.parse_args()
        # print("SAATU PYYNTÖ")
        # data = request.get_json(force=True)
        # print(data)

        # cards = data['cards']
        # tasks = Task.query.all()
        # d = {}
        # d['cards_modified'] = []
        # something_changed = False

        # card_list = []
        # for i in cards:
        #     print(i['id'])
        #     tehtava = Task.query.filter_by(id=i['id']).first()
        #     print("Tehtävä: ", tehtava)
        #     if tehtava is not None:
        #         if tehtava.title != i['title']:
        #             print("Otsikko muuttui")
        #             something_changed = True
        #             tehtava.title = i['title']
        #         if tehtava.description != i['description']:
        #             print("kuvaus muuttui")
        #             something_changed = True
        #             tehtava.description = i['description']
        #         if tehtava.position != i['position']:
        #             print("Paikka muuttui")
        #             something_changed = True
        #             tehtava.position = i['position']

        #         print("tehtava lopussa")
        #         if something_changed:
        #             dc = {
        #                 'description': tehtava.description,
        #                 'id': tehtava.id,
        #                 'position': tehtava.position,
        #                 'priority': i['priority'],
        #                 'title': tehtava.title
        #             }
        #             d['cards_modified'].append(dc)
        #         #if tehtava.priority != i['priority']:
        #         #    tehtava.priority = i['priority']
        #         #db.session.merge(tehtava)
        #         db.session.commit()
        
        # return jsonify(d)
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
