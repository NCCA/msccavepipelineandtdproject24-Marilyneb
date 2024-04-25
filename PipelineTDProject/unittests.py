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
        self.app.config['SECRET_KEY'] = 'secret-key' 
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
            test_user = User(username='testuser')
            test_user.set_password('testpassword')
            db.session.add(test_user)
            db.session.commit()
            self.client.post('/login', data=dict(
                username='testuser',
                password='testpassword'
            ), follow_redirects=True)

            response = self.client.get('/profile/testuser', follow_redirects=True)
            self.assertIn(b'testuser', response.data)
    

    def test_upload(self):
        with self.app.app_context():
            test_user = User(username='testuser')
            test_user.set_password('testpassword')
            db.session.add(test_user)
            db.session.commit()
            self.client.post('/login', data=dict(
                username='testuser',
                password='testpassword'
            ), follow_redirects=True)

            with open('uploads/test.jpg', 'rb') as f:
                data = {'file': (f, 'test.jpg')}
                response = self.client.post('/upload', data=data)

            self.assertEqual(response.status_code, 200)

    def test_upload_file_with_tags(self):
        with self.app.app_context():
            # Create a test user
            test_user = User(username='testuser')
            test_user.set_password('testpassword')
            db.session.add(test_user)
            db.session.commit()

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

            self.assertEqual(response.status_code, 200)

            self.assertIsNotNone(Tag.query.filter_by(name='tag1').first())
            self.assertIsNotNone(Tag.query.filter_by(name='tag2').first())
            self.assertIsNotNone(Tag.query.filter_by(name='tag3').first())

            asset = Asset.query.filter_by(name='my_file.txt').first()
            self.assertIsNotNone(asset)
            self.assertIn('tag1', [tag.name for tag in asset.tags])
            self.assertIn('tag2', [tag.name for tag in asset.tags])
            self.assertIn('tag3', [tag.name for tag in asset.tags])

if __name__ == '__main__':
    unittest.main()