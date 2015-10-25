


################### MODELS  #######################
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    bucket = db.relationship('BucketList', backref='owner', lazy='dynamic')


    def to_json(self):

        return {
            "id": self.id,
            "username": self.username,
            "date_created": self.date_created.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def __repr__(self):
        return "<User(username='%s', email='%s')>" % (self.username,
         self.email)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=42000):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user


class BucketList(db.Model):
    __tablename__ = 'Bucketlists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    date_created = db.Column(db.DateTime, default=datetime.datetime.now())
    date_modified = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.utcnow())   
    created_by = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    items = db.relationship('Item', backref='bucketlist', cascade="all, delete-orphan",lazy='dynamic')


    #method to be defined here...
    #"items": [row.to_json() for row in self.items],
    def to_json(self):
        """Converts model object into dict to ease Serialization
        """
        return {
            "id": self.id,
            "name": self.name,
            "items_count": len(self.items.all()),
            "date_created": self.date_created.strftime("%Y-%m-%d %H:%M:%S"),
            "date_modified": self.date_modified.strftime("%Y-%m-%d %H:%M:%S"),
            "created_by": self.created_by,
        }



class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(64))
    date_created = db.Column(db.DateTime,  default=datetime.datetime.utcnow())
    date_modified = db.Column(db.DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())   
    done = db.Column(db.Boolean, default=False) 

    bucketlist_id = db.Column(db.Integer, db.ForeignKey('Bucketlists.id'), nullable=False)
    


    def to_json(self):
        """Converts model object into dict to ease Serialization
        """
        return {
            "id": self.id,
            "name": self.name,
            "date_created": self.date_created.strftime("%Y-%m-%d %H:%M:%S"),
            "date_modified": self.date_modified.strftime("%Y-%m-%d %H:%M:%S"),
            "done": self.done,
        }

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

