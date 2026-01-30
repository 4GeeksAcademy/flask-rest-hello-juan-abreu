from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    is_active = db.Column(db.Boolean(), nullable=False, default=True)
    
    # Relaciones
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active
            # NO incluir password por seguridad
        }


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relaciones
    media = db.relationship('Media', backref='post', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Post {self.id}>'

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "author": self.author.serialize() if self.author else None,
            "media": [m.serialize() for m in self.media],
            "comments": [c.serialize() for c in self.comments]
        }


class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    url = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Media {self.id}>'

    def serialize(self):
        return {
            "id": self.id,
            "post_id": self.post_id,
            "url": self.url
        }


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment_text = db.Column(db.String(300), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Comment {self.id}>'

    def serialize(self):
        return {
            "id": self.id,
            "comment_text": self.comment_text,
            "post_id": self.post_id,
            "user_id": self.user_id,
            "author": self.author.serialize() if self.author else None
        }


class Follower(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f'<Follower {self.id}>'

    def serialize(self):
        return {
            "id": self.id
        }


class Followers(db.Model):
    follower_id = db.Column(db.Integer, db.ForeignKey('follower.id'), primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)

    def __repr__(self):
        return f'<Followers follower={self.follower_id} user={self.user_id}>'

    def serialize(self):
        return {
            "follower_id": self.follower_id,
            "user_id": self.user_id
        }