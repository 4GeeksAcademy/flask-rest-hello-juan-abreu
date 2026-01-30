import os
from flask_admin import Admin
from models import db, User, Post, Media, Comment, Follower, Followers
from flask_admin.contrib.sqla import ModelView

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='Instagram Database Admin', template_mode='bootstrap3')

    # Agregar modelos al panel de administración
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Post, db.session))
    admin.add_view(ModelView(Media, db.session))
    admin.add_view(ModelView(Comment, db.session))
    admin.add_view(ModelView(Follower, db.session))
    admin.add_view(ModelView(Followers, db.session))