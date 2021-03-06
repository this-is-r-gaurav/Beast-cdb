from flask_restplus import Resource, Namespace, fields
from flask import jsonify, g
from flask import request

from flask_httpauth import HTTPTokenAuth
import src.models.api.guser as guser
from src.models.api.dot.Admin import AdminAPI

admin_namespace = Namespace('DOT Admin', 'There are Various Operations regarding Admin')

auth = HTTPTokenAuth(scheme='Token')


@auth.verify_token
def verify_token(token):
    if token in guser.tokens:
        g.current_user = guser.tokens[token]

        return True
    return False


admin_model = admin_namespace.model('Admin', {
    'username': fields.String(required=True, description='Admin Username'),
    'password': fields.String(required=True, description='Admin Password'),
    'name': fields.String(required=True, description='Admin Name'),
    'privileges': fields.String(required=True, description='Admin Privileges')
})


@admin_namespace.route('/')
class ListUser(Resource):
    def get(self):
        users = AdminAPI.get_all_admin()
        return jsonify({"data": users})

    @admin_namespace.doc(params={
        'username': {'in': 'formData', 'description': 'Admin Username', 'required': 'True'},
        'password': {'in': 'formData', 'description': 'Admin Password', 'required': 'True'},
        'name': {'in': 'formData', 'description': 'Admin Name', 'required': 'True'},

        'privileges': {'in': 'formData', 'description': 'User Privileges', 'required': 'True'}
    })
    def post(self):
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        privileges = request.form['privileges']
        if AdminAPI.create_new_user(username=username, name=name, password=password, privileges=privileges):
            return {'msg': 'Admin created Successfully'}, 201
        else:
            return {'msg': 'There is some error'}, 400


@admin_namespace.route('/<string:admin_id>')
class SingleUser(Resource):
    def get(self, admin_id):
        return jsonify(AdminAPI.get_admin_by_admin_id(admin_id))


@admin_namespace.route('/login')
class Authorize(Resource):
    @admin_namespace.doc(params={
        'username': {'in': 'formData', 'description': 'Username of Dot Admin', 'required': 'True'},
        'password': {'in': 'formData', 'description': 'Password of Dot Admin', 'required': 'True'}})
    def post(self):
        username = request.form['username']
        password = request.form['password']
        data = AdminAPI.authenticate_admin(username, password)
        if data:
            return {
                'status': 'success',
                'data': [AdminAPI.authenticate_admin(username, password)]
            }


@admin_namespace.route('/list-by-count')
class ListSimCount(Resource):
    @admin_namespace.doc(params={
        'count': {'in': 'formData', 'description': 'The no of count you want to query', 'required': 'True'}})
    def post(self):
        count = request.form['count']
        cluster_data = AdminAPI.gets_user_by_count(count)
        return {"msg": "successful",
                "data": [{'aadhaar': key, 'count': cluster_data[key]} for key in
                         cluster_data.keys()]} if cluster_data is not None or False else {'msg': 'No User'}


@admin_namespace.route('/list-by-lsa')
class ListSimlsa(Resource):
    @admin_namespace.doc(params={
        'lsa': {'in': 'formData', 'description': 'Local Service Area', 'required': 'True'}})
    def post(self):
        lsa = request.form['lsa']
        cluster_data = AdminAPI.list_users_by_lsa(lsa)
        return {"msg": "successful",
                "data": [{'aadhaar': key, 'count': cluster_data[key]} for key in
                         cluster_data.keys()]} if cluster_data is not None or False else {'msg': 'No User'}
