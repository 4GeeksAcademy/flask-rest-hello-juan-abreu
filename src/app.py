"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Post, Media, Comment, Follower, Followers

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


# ==================== USER ENDPOINTS ====================

@app.route('/users', methods=['GET'])
def get_users():
    """Obtener todos los usuarios"""
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Obtener un usuario específico"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.serialize()), 200


@app.route('/users', methods=['POST'])
def create_user():
    """Crear un nuevo usuario"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password are required"}), 400
    
    # Verificar si el email ya existe
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"error": "Email already exists"}), 400
    
    new_user = User(
        email=data['email'],
        password=data['password'],  # En producción, deberías hashear la contraseña
        is_active=data.get('is_active', True)
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify(new_user.serialize()), 201


# ==================== POST ENDPOINTS ====================

@app.route('/posts', methods=['GET'])
def get_posts():
    """Obtener todos los posts"""
    posts = Post.query.all()
    return jsonify([post.serialize() for post in posts]), 200


@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Obtener un post específico"""
    post = Post.query.get_or_404(post_id)
    return jsonify(post.serialize()), 200


@app.route('/posts', methods=['POST'])
def create_post():
    """Crear un nuevo post"""
    data = request.get_json()
    
    if not data or 'user_id' not in data:
        return jsonify({"error": "user_id is required"}), 400
    
    # Verificar que el usuario existe
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    new_post = Post(user_id=data['user_id'])
    db.session.add(new_post)
    db.session.commit()
    
    return jsonify(new_post.serialize()), 201


@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Eliminar un post"""
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({"message": "Post deleted successfully"}), 200


# ==================== MEDIA ENDPOINTS ====================

@app.route('/media', methods=['POST'])
def create_media():
    """Agregar media a un post"""
    data = request.get_json()
    
    if not data or 'post_id' not in data or 'url' not in data:
        return jsonify({"error": "post_id and url are required"}), 400
    
    # Verificar que el post existe
    post = Post.query.get(data['post_id'])
    if not post:
        return jsonify({"error": "Post not found"}), 404
    
    new_media = Media(
        post_id=data['post_id'],
        url=data['url']
    )
    
    db.session.add(new_media)
    db.session.commit()
    
    return jsonify(new_media.serialize()), 201


# ==================== COMMENT ENDPOINTS ====================

@app.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_post_comments(post_id):
    """Obtener comentarios de un post"""
    post = Post.query.get_or_404(post_id)
    return jsonify([comment.serialize() for comment in post.comments]), 200


@app.route('/comments', methods=['POST'])
def create_comment():
    """Crear un comentario en un post"""
    data = request.get_json()
    
    if not data or 'post_id' not in data or 'user_id' not in data or 'comment_text' not in data:
        return jsonify({"error": "post_id, user_id, and comment_text are required"}), 400
    
    # Verificar que el post y usuario existen
    post = Post.query.get(data['post_id'])
    user = User.query.get(data['user_id'])
    
    if not post:
        return jsonify({"error": "Post not found"}), 404
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    new_comment = Comment(
        comment_text=data['comment_text'],
        post_id=data['post_id'],
        user_id=data['user_id']
    )
    
    db.session.add(new_comment)
    db.session.commit()
    
    return jsonify(new_comment.serialize()), 201


@app.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """Eliminar un comentario"""
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({"message": "Comment deleted successfully"}), 200


# ==================== FOLLOWER ENDPOINTS ====================

@app.route('/users/<int:user_id>/followers', methods=['GET'])
def get_user_followers(user_id):
    """Obtener seguidores de un usuario"""
    user = User.query.get_or_404(user_id)
    followers = Followers.query.filter_by(user_id=user_id).all()
    return jsonify([f.serialize() for f in followers]), 200


@app.route('/follow', methods=['POST'])
def follow_user():
    """Seguir a un usuario"""
    data = request.get_json()
    
    if not data or 'follower_id' not in data or 'user_id' not in data:
        return jsonify({"error": "follower_id and user_id are required"}), 400
    
    # Verificar que ambos existen
    follower = Follower.query.get(data['follower_id'])
    user = User.query.get(data['user_id'])
    
    if not follower:
        return jsonify({"error": "Follower not found"}), 404
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Verificar que no está siguiendo ya
    existing = Followers.query.filter_by(
        follower_id=data['follower_id'],
        user_id=data['user_id']
    ).first()
    
    if existing:
        return jsonify({"error": "Already following"}), 400
    
    new_follow = Followers(
        follower_id=data['follower_id'],
        user_id=data['user_id']
    )
    
    db.session.add(new_follow)
    db.session.commit()
    
    return jsonify(new_follow.serialize()), 201


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)