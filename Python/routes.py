import os
from flask import render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from flask import send_from_directory
from models import User, Asset, Tag

app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            return 'Username already exists', 400
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('profile', username=username))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile/<username>')
def profile(username):
    return render_template('profile.html', username=username)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part', 400
        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        asset = Asset(name=filename, user_id=current_user.id)
        db.session.add(asset)

        tags = request.form.get('tags', '').split(',')
        for tag_name in tags:
            tag = Tag.query.filter_by(name=tag_name.strip()).first()
            if tag is None:
                tag = Tag(name=tag_name.strip())
                db.session.add(tag)
            asset.tags.append(tag)

        db.session.commit()

        return 'File uploaded successfully', 200
    return render_template('upload.html')

@app.route('/assets', methods=['GET'])
def get_assets():
    assets = Asset.query.all()
    asset_list = [{'name': asset.name, 'tags': [tag.name for tag in asset.tags]} for asset in assets]
    return {'assets': asset_list}, 200

@app.route('/assets/<filename>')
def get_asset(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/search/<tag>', methods=['GET'])
def search_by_tag(tag):
    tag = Tag.query.filter_by(name=tag).first()
    if tag is None:
        return 'No assets found for this tag', 404
    assets = [asset.name for asset in tag.assets]
    return {'assets': assets}, 200


@app.route('/download/<filename>', methods=['GET'])
def download_asset(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)