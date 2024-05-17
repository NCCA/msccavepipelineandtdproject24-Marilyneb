import unittest
import os
import io
from app import app, db
from models import User, Asset, Tag
import shutil
from flask_login import login_user
from flask_login import current_user
from io import BytesIO


class TestUserModel(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SECRET_KEY'] = 'your-secret-key' 
        self.db = db
        with self.app.app_context():
            self.db.create_all()
        self.client = self.app.test_client()
        
    def tearDown(self):
        with self.app.app_context():
            self.db.session.remove()
            self.db.drop_all()

    def test_password_hashing(self):
        with self.app.app_context():
            u = User(username='john')
            u.set_password('cat')
            self.assertFalse(u.check_password('dog'))
            self.assertTrue(u.check_password('cat'))

    def test_register(self):
        with self.app.app_context():
            response = self.client.post('/register', data=dict(
                username='testuser',
                password='testpassword'
            ), follow_redirects=True)
            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(response.status_code, 200)


    def test_login(self):
        with self.app.app_context():

            test_user = User(username='testuser')
            test_user.set_password('testpassword')
            db.session.add(test_user)
            db.session.commit()

            response = self.client.post('/login', data=dict(
                username='testuser',
                password='testpassword'
            ), follow_redirects=True)


            print(response.data)

            self.assertIn(b'Profile', response.data)
            
    def test_logout(self):
        with self.app.app_context():

            test_user = User(username='testuser')
            test_user.set_password('testpassword')
            db.session.add(test_user)
            db.session.commit()
            self.client.post('/login', data=dict(
                username='testuser',
                password='testpassword'
            ), follow_redirects=True)

            response = self.client.get('/logout', follow_redirects=True)
            self.assertIn(b'Login', response.data)


    def test_profile_page(self):
        with self.app.app_context():
            # Create a test user and log them in
            test_user = User(username='testuser')
            test_user.set_password('testpassword')
            db.session.add(test_user)
            db.session.commit()
            self.client.post('/login', data=dict(
                username='testuser',
                password='testpassword'
            ), follow_redirects=True)

            # Access the profile page
            response = self.client.get('/profile/testuser', follow_redirects=True)

            # Check that the response includes the username
            self.assertIn(b'testuser', response.data)
    

    def test_upload(self):
        with self.app.app_context():
            # Create a test user and log them in
            test_user = User(username='testuser')
            test_user.set_password('testpassword')
            db.session.add(test_user)
            db.session.commit()
            self.client.post('/login', data=dict(
                username='testuser',
                password='testpassword'
            ), follow_redirects=True)

            # Open the file in binary mode
            with open('uploads/test.jpg', 'rb') as f:
                data = {'file': (f, 'test.jpg')}
                response = self.client.post('/upload', data=data)

            # Check the response
            self.assertEqual(response.status_code, 200)

    def test_upload_file_with_tags(self):
        with self.app.app_context():
            # Create a test user
            test_user = User(username='testuser')
            test_user.set_password('testpassword')
            db.session.add(test_user)
            db.session.commit()

            # Log in as the test user
            with self.client:
                response = self.client.post('/login', data=dict(
                    username='testuser',
                    password='testpassword'
                ), follow_redirects=True)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(current_user.username, 'testuser')

                response = self.client.post('/upload', data={
                    'file': (BytesIO(b'my file contents'), 'my_file.txt'),
                    'tags': 'tag1, tag2, tag3'
                })

            # Check that the upload was successful
            self.assertEqual(response.status_code, 200)

            # Check that the tags were created
            self.assertIsNotNone(Tag.query.filter_by(name='tag1').first())
            self.assertIsNotNone(Tag.query.filter_by(name='tag2').first())
            self.assertIsNotNone(Tag.query.filter_by(name='tag3').first())

            # Check that the tags were associated with the uploaded file
            asset = Asset.query.filter_by(name='my_file.txt').first()
            self.assertIsNotNone(asset)
            self.assertIn('tag1', [tag.name for tag in asset.tags])
            self.assertIn('tag2', [tag.name for tag in asset.tags])
            self.assertIn('tag3', [tag.name for tag in asset.tags])

    def test_get_assets(self):
        with self.app.app_context():
            # Create a test user and log them in
            test_user = User(username='testuser')
            test_user.set_password('testpassword')
            db.session.add(test_user)
            db.session.commit()
            self.client.post('/login', data=dict(
                username='testuser',
                password='testpassword'
            ), follow_redirects=True)

            # Create a test asset and add it to the database
            test_asset = Asset(name='test_asset')
            db.session.add(test_asset)
            db.session.commit()

            # Access the /assets route
            response = self.client.get('/assets', follow_redirects=True)

            # Check that the response includes the asset name
            self.assertIn(b'test_asset', response.data)

    def test_download_asset(self):
        with self.app.app_context():
            # Create a test user and log them in
            test_user = User(username='testuser')
            test_user.set_password('testpassword')
            db.session.add(test_user)
            db.session.commit()
            self.client.post('/login', data=dict(
                username='testuser',
                password='testpassword'
            ), follow_redirects=True)

            # Create a test asset and add it to the database
            test_asset = Asset(name='test_asset')
            db.session.add(test_asset)
            db.session.commit()

            # Access the /download/<filename> route
            response = self.client.get(f'/download/{test_asset.name}', follow_redirects=True)

            # Check that the response status code is 200 (OK)
            self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()