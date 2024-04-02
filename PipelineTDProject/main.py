import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['UPLOAD_FOLDER'] = os.path.dirname(os.path.abspath(__file__))
db = SQLAlchemy(app)

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    filename = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tags = db.relationship('Tag', backref='asset', lazy=True)  

    def __repr__(self):
        return '<Asset %r>' % self.filename

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    assets = db.relationship('Asset', backref='user', lazy=True) 

    def __repr__(self):
        return '<User %r>' % self.username

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)

    def __repr__(self):
        return '<Tag %r>' % self.name

@app.route('/')
def hello_world():
    return 'Hello, World!'

def hash_password(password):
    return generate_password_hash(password, method='pbkdf2:sha256')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Invalid request. Ensure JSON contains username, email, and password fields.'}), 400

    username = data['username']
    email = data['email']
    password = data['password']

    hashed_password = hash_password(password)
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Registration successful'}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        return jsonify({'message': 'Login successful'}), 200

    return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_asset = Asset(type='model', filename=filename, user_id=1)  
        db.session.add(new_asset)
        db.session.commit()

        return jsonify({'message': 'File successfully uploaded'}), 200
    else:
        return jsonify({'message': 'Allowed file types are png, jpg, jpeg, gif'}), 400

@app.route('/tag', methods=['POST'])
def add_tag():
    data = request.get_json()
    asset_id = data['asset_id']
    tag_name = data['tag_name']

    new_tag = Tag(name=tag_name, asset_id=asset_id)
    db.session.add(new_tag)
    db.session.commit()

    return jsonify({'message': 'Tag added successfully'}), 200

@app.route('/search/asset_type', methods=['GET'])
def search_by_asset_type():
    asset_type = request.args.get('asset_type')
    assets = Asset.query.filter_by(type=asset_type).all()

    assets = [asset.filename for asset in assets]

    return jsonify({'assets': assets}), 200