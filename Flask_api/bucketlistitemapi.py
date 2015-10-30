'''Script Used for BucketlistItem Api Accesspoint. '''

from Flask_api import app, auth, db
from .models import BucketList, Item
from .errors import bad_request
from flask import request, jsonify, g
from datetime import datetime


@app.route("/bucketlists/<int:id>/items/", methods=['POST'])
@auth.login_required #create item in bucketlist
def addnew_bucketlistitem(id):

    ''' create a bucket list item. '''

    bucketlist = BucketList.query.\
                filter_by(created_by=g.user.username).\
                filter_by(id=id).first()

    if not bucketlist:
        return bad_request('bucket list with id:{} was not found' .format(id))

    json_data = request.get_json()
    name, done = json_data['name'], json_data['done']            
    item = Item(name=name, done=True, date_modified=datetime.utcnow())
    item.bucketlist_id=bucketlist.id
    item.save()

    return jsonify({'Item':item.to_json()})


@app.route("/bucketlists/<int:id>/items/<int:item_id>", methods=['PUT', 'DELETE'])
@auth.login_required
def delete_and_update(id, item_id):

    '''Delete and update a bucketlist item. '''
    
    bucketlist = BucketList.query.\
                filter_by(created_by=g.user.username).\
                filter_by(id=id).first()
    if not bucketlist:
        return bad_request('bucket list with id:{} was not found' .format(id))
    
    item =Item.query.get(item_id)
    if not item:
            return bad_request('bucket list with id:{} was not found' .format(item_id))

    if request.method == 'PUT':

        if item.bucketlist_id == bucketlist.id:
            json_data = request.get_json()
            name, done = json_data['name'], json_data['done']
            item.name=name 
            item.done=done
            item.date_modified=datetime.utcnow()

            item.bucketlist_id=bucketlist.id
            item.save()

            return jsonify({'Item':item.to_json()})

    if request.method == 'DELETE':
        item.delete()

        return jsonify({'message': 'bucketlist successfully deleted'})
