
class BucketList(db.Model):
    __tablename__ = 'Bucketlists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    date_created = db.Column(db.DateTime, default=datetime.datetime.now())
    date_modified = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())   
    created_by = db.Column(db.String(64))

    #itemdata=db.relationship('Item')


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    date_created = db.Column(db.DateTime,  default=datetime.datetime.now())
    date_modified = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())   
    done = db.Column(db.Boolean, default=False) 

    bucketlist_id = db.Column(db.Integer, db.ForeignKey('Bucketlists.id'), nullable=False)
    bucketlist = db.relationship('BucketList', backref=db.backref('items', lazy='dynamic'))




@auth.login_required





class UserSchema(ma.Schema):

    class Meta:
        # Fields to expose
        fields = ('id', 'username', 'email', 'date_created', '_links')
        ordered = True

        # Smart hyperlinking
    _links = ma.Hyperlinks({
        'self': ma.URLFor('author_detail', id='<id>'),
        'collection': ma.URLFor('authors')
    })


class ListSchema(ma.Schema):
    
    class Meta:

        items = fields.Nested(ItemSchema)
        fields = ('id', 'name','items', 'date_created', 'date_modified', 'created_by',)
        ordered = True

class ItemSchema(ma.Schema):
    
    class Meta:

        fields = ('id', 'name', 'date_created', 'date_modified', 'done')
        ordered = True

#####################################################
def list_object_transform(list_data):
    result_data = []
    for item in list_data:
        result_set = item.to_json()
        result_data.append(result_set)
    return result_data



