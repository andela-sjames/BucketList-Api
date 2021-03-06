'''Script Used for Bucketlist Api Accesspoint. '''

from Flask_api import app, auth, db
from .models import BucketList
from .errors import bad_request, not_allowed
from flask import request, jsonify, g, url_for
from datetime import datetime


@app.route("/bucketlists/", methods=['GET','POST'])
@auth.login_required
def create_and_getbucketlist():

    '''User can view and create bucketlist. '''
    
    #set page to 1 and limit to 20 by default.
    page = request.args.get('page', 1, type=int)# get page
    limit = request.args.get('limit', app.config['PERPAGE_MIN_LIMIT'],type = int) #get limit
    limit = limit if limit <= app.config['PERPAGE_MAX_LIMIT'] else app.config['PERPAGE_MAX_LIMIT'] 

    q = request.args.get('q')#get q search value and use if available

    if request.method == 'GET':
        if q:
            alluserbucketlist = BucketList.query.filter_by(created_by=g.user.username).filter(BucketList.name.ilike('%{0}%'.format(q)))
        else:
            alluserbucketlist = BucketList.query.filter_by(created_by=g.user.username)

        #pagination of view by default.
        pagination = alluserbucketlist.paginate(page, per_page=limit, 
            error_out=False)
        buckets=pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for('create_and_getbucketlist', 
                page=page-1,
                limit = 2, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('create_and_getbucketlist', 
                page=page+1,
                limit = limit, _external=True)
            
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

        bucketlist = BucketList(name=json_data['name'],
            created_by=g.user.username, user_id=g.user.id)
        bucketlist.save()

        return jsonify({'bucketlist':bucketlist.to_json()})
        

@app.route("/bucketlists/<int:id>", methods=['GET', 'PUT', 'DELETE'])
@auth.login_required #get single bucketlist item
def get_delete_putbucketlist(id):

    ''' Get bucket list by id's'''

    bucketlist = BucketList.query.\
                filter_by(created_by=g.user.username).\
                filter_by(id=id).first()
    if not bucketlist:
            return not_allowed()

    page = request.args.get('page', 1, type=int)# get page
    limit = request.args.get('limit', app.config['PERPAGE_MIN_LIMIT'],type = int) #get limit
    limit = limit if limit <= app.config['PERPAGE_MAX_LIMIT'] else app.config['PERPAGE_MAX_LIMIT']

    if request.method == 'GET':
        
        itemsquerydataset = bucketlist.items
        pagination =itemsquerydataset.paginate(page, 
            per_page=limit, error_out=False)
        bucket_items=pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for('get_delete_putbucketlist', 
                id = bucketlist.id,page=page-1, 
                limit = limit, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('get_delete_putbucketlist',
                id = bucketlist.id ,page=page+1, 
                limit = limit, _external=True)
        
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
            bucketlist.save()

            return jsonify({'bucketlist':bucketlist.to_json()})
        
    if request.method == 'DELETE':
        #dynamicall delete all related items to bucketlist.
        bucketlist.delete()

        return jsonify({'message': 'bucketlist successfully deleted'})

        