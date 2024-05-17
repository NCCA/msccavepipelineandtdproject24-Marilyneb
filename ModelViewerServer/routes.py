import os
from flask import render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
from flask import send_from_directory, session, flash
from models import User, Asset, Tag, load_user

# Set the upload folder configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DEBUG'] = True


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if the username already exists
        user = User.query.filter_by(username=username).first()
        if user:
            return 'Username already exists', 400
        # Create a new user and add them to the database
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Current user: "+str(current_user))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        print("Before If user check")
        if user and user.check_password(password):
            print("After If user check")
            login_user(user, remember=True)
            print("Current user: "+str(current_user))
            print("User authenticated: "+str(current_user.is_authenticated))
            return redirect(url_for('profile', username=username))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/profile/<username>')
def profile(username):
    # get user data based on username
    return render_template('profile.html', username=username)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if(False):
        print("error")
        return 'Unauthorized', 401
    else:
        print("Current user: " + str(current_user))
        if request.method == 'POST':
            if 'file' not in request.files:
                return 'No file part', 400
            file = request.files['file']
            if file.filename == '':
                return 'No selected file', 400
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Create a new asset
            asset = Asset(name=filename, user_id=current_user.id)
            db.session.add(asset)

            # Handle the tags
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
        asset_list = []
        return {'assets': asset_list}, 200

    asset_list = [{'name': asset.name, 'tags': [tag.name for tag in asset.tags]} for asset in tag.assets]

    return {'assets': asset_list}, 200


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/view_model/<filename>')
def view_model(filename):

    return render_template('view_model.html', model_name=filename)


@app.route('/debug_session')
def debug_session():
    print(session)
    return 'Session Debugging'
