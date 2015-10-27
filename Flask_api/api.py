

from Flask_api import app, auth, db
from .models import User, BucketList, Item
from .errors import not_found, bad_request,  precondition_failed
from sqlalchemy.exc import IntegrityError
from flask import request, jsonify, g, url_for
from datetime import datetime



@app.route('/auth/login', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if not username  or not password:
        return bad_request('Missing arguments/parameters given')
    if User.query.filter_by(username=username).first() is not None:
        return bad_request('User already exists')
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({ 'user':user.to_json(),
                        'request_token':url_for('request_token'), 
                        'User':url_for('get_user', username = user.username,  _external =True) }),201)
#{'Location': url_for('get_user', id = user.id, _external = True)}

@app.route('/auth/token')
@auth.login_required
def request_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii')})

@app.route('/user/<username>/')
@auth.login_required
def get_user(username):
    '''Return a user'''
    user = User.query.filter_by(username=username).first()
    if not user:
        return unauthorized()
    return jsonify({'user': user.to_json()})



@app.route("/bucketlists", methods=['GET','POST'])
@auth.login_required
def create_and_getbucketlist():

    page = request.args.get('page', 1, type=int)# get page
    limit = request.args.get('limit', app.config['PERPAGE_MIN_LIMIT'],type = int) #get limit
    limit = limit if limit <= app.config['PERPAGE_MAX_LIMIT'] else app.config['PERPAGE_MAX_LIMIT'] 

    q = request.args.get('q')  #get q search value and use if available

    if request.method == 'GET':
        if q:
            alluserbucketlist = BucketList.query.filter_by(created_by=g.user.username).filter(BucketList.name.ilike('%{0}%'.format(q)))
        else:
            alluserbucketlist = BucketList.query.filter_by(created_by=g.user.username)
            
        if not alluserbucketlist:
            return jsonify({ 'message':'No bucketlist to display' })

        pagination = alluserbucketlist.paginate(page, per_page=limit, 
            error_out=False)
        buckets=pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for('create_and_getbucketlist', page=page-1,limit = 2, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('create_and_getbucketlist', page=page+1,limit = limit, _external=True)
            
        return jsonify({
            'bucketlist': [bucket.to_json() for bucket in buckets], 
            'prev': prev,
            'next': next,
            'count': pagination.total
        })

    if request.method == 'POST':
        json_data = request.get_json()
        if not json_data['name']:
            return bad_request('No input data provided')

        bucketList = BucketList(name=json_data['name'],created_by=g.user.username, user_id=g.user.id)
        db.session.add(bucketList)
        db.session.commit()

        bucketid = BucketList.query.get(bucketList.id)
        return jsonify({'bucketlist':bucketid.to_json()})
        

@app.route("/bucketlists/<int:id>", methods=['GET', 'PUT', 'DELETE'])
@auth.login_required #get single bucketlist item
def get_delete_putbucketlist(id):

    bucketlist = BucketList.query.\
                filter_by(created_by=g.user.username).\
                filter_by(id=id).first()
    if not bucketlist:
            return not_found('bucket list with id:{} was not found' .format(id))

    page = request.args.get('page', 1, type=int)# get page
    limit = request.args.get('limit', app.config['PERPAGE_MIN_LIMIT'],type = int) #get limit
    limit = limit if limit <= app.config['PERPAGE_MAX_LIMIT'] else app.config['PERPAGE_MAX_LIMIT']

    if request.method == 'GET':
        if bucketlist:
            itemsquerydataset = bucketlist.items
            pagination =itemsquerydataset.paginate(page, per_page=limit, error_out=False)
            bucket_items=pagination.items
            prev = None
            if pagination.has_prev:
                prev = url_for('get_delete_putbucketlist', id = bucketlist.id,page=page-1, limit = limit, _external=True)
            next = None
            if pagination.has_next:
                next = url_for('get_delete_putbucketlist',id = bucketlist.id ,page=page+1, limit = limit, _external=True)
            
            buckets=bucketlist.to_json()
            buckets['items'] = [ itemsqueryset.to_json() for itemsqueryset in bucket_items ]

            return jsonify({
                'bucketlist': buckets, 
                'prev': prev,
                'next': next,
                'count': pagination.total
            })
        
    if request.method == 'PUT':        
        if bucketlist:
            json_data = request.get_json()
            bucketlist.name=json_data['name']
            bucketlist.date_modified=datetime.utcnow()
            db.session.add(bucketlist)
            db.session.commit()
            bucket=BucketList.query.get(id)

            return jsonify({'bucketlist':bucketlist.to_json()})
        
    if request.method == 'DELETE':
        if bucketlist:
            db.session.add(bucketlist)
            db.session.delete(bucketlist)
            db.session.commit()

            return jsonify({'message': 'bucketlist successfully deleted'})

        

@app.route("/bucketlists/<int:id>/items", methods=['POST'])
@auth.login_required #create item in bucketlist
def addnew_bucketlistitem(id):

    bucketlist = BucketList.query.\
                filter_by(created_by=g.user.username).\
                filter_by(id=id).first()

    if not bucketlist:
        return bad_request('bucket list with id:{} was not found' .format(id))

    json_data = request.get_json()
    if not json_data:
        return bad_request('No or incomplete input data provided')
    
    name, done = json_data['name'], json_data['done']    
    if done == 'TRUE' or 'true':        
        item = Item(name=name, done=True, date_modified=datetime.utcnow())
    else:
        item =Item(name=name,done=False, date_modified=datetime.utcnow())
        
    item.bucketlist_id=bucketlist.id
    db.session.add(item)
    db.session.commit()
    
    added_item=Item.query.get(item.id)
    return jsonify({'Item':added_item.to_json()})

@app.route("/bucketlists/<int:id>/items/<int:item_id>", methods=['PUT', 'DELETE'])
@auth.login_required
def delete_and_update(id, item_id):
    
    bucketlist = BucketList.query.\
                filter_by(created_by=g.user.username).\
                filter_by(id=id).first()
    if not bucketlist:
        return bad_request('bucket list with id:{} was not found' .format(id))
    
    item =Item.query.get(item_id)
    if not item:
            return bad_request('bucket list with id:{} was not found' .format(item_id))

    if request.method == 'PUT':
        if item:
            if item.bucketlist_id == bucketlist.id:
                json_data = request.get_json()
                name, done = json_data['name'], json_data['done']
                item.name=name 
                item.done=done
                item.date_modified=datetime.utcnow()

                item.bucketlist_id=bucketlist.id
                db.session.add(item)
                db.session.commit()

                responseitem = Item.query.get(item.id)
                return jsonify({'Item':responseitem.to_json()})
        else:
            return bad_request('item not related to bucketlist')

    if request.method == 'DELETE':
        if item:

            db.session.add(item)
            db.session.delete(item)
            db.session.commit()

        return jsonify({'message': 'bucketlist successfully deleted'})
