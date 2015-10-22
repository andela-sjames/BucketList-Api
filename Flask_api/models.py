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

class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('email', 'date_created', '_links')
        ordered = True
    # Smart hyperlinking
    _links = ma.Hyperlinks({
        'self': ma.URLFor('author_detail', id='<id>'),
        'collection': ma.URLFor('authors')
    })

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@app.route('/api/users/')
def users():
    all_users = User.all() # make your python query
    result = users_schema.dump(all_users) # serialize your query
    return jsonify(result.data) #jsonify it
    # OR
    # return user_schema.jsonify(all_users)

@app.route('/api/users/<id>')
def user_detail(id):
    user = User.get(id) # query database
    return user_schema.jsonify(user) # jsonify it
