import json
from flask_testing import TestCase
from main import app, db, User, hash_password
from main import Asset  

class MyTest(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_hello_world(self):
        response = self.client.get('/')
        self.assert200(response)
        self.assertEqual(response.data, b'Hello, World!')

    def test_user_registration(self):
        user = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword"
        }

        response = self.client.post('/register', json=user)
        self.assert200(response)
        self.assertIn(b'Registration successful', response.data)

        user_in_db = User.query.filter_by(username=user['username']).first()
        self.assertIsNotNone(user_in_db)
        self.assertEqual(user_in_db.username, user['username'])
        self.assertEqual(user_in_db.email, user['email'])
        self.assertNotEqual(user_in_db.password, user['password'])  

    def test_invalid_registration_request(self):
        invalid_data = {}  
        response = self.client.post('/register', json=invalid_data)
        self.assert400(response)
        self.assertIn(b'Invalid request', response.data)
    
    def test_user_login(self):
        self.test_user_registration()

        credentials = {
            "username": "testuser",
            "password": "testpassword"
         }

        response = self.client.post('/login', json=credentials)

        self.assert200(response)

        self.assertIn(b'Login successful', response.data)

    def test_asset_upload(self):
        asset_file = open('test_asset.jpg', 'rb')  
        data = {
            'file': (asset_file, 'test_asset.jpg')
        }

        response = self.client.post('/upload', data=data, content_type='multipart/form-data')

        self.assert200(response)


        self.assertIn(b'File successfully uploaded', response.data)

        asset_file.close()  

    def test_add_tag(self):
      
        self.test_asset_upload()

        asset = Asset.query.first()

        if asset is None:
            self.fail("No asset was uploaded")
        tag_data = {
            "asset_id": asset.id,  
            "tag_name": "testtag"
        }

        response = self.client.post('/tag', json=tag_data)

        self.assert200(response)

        self.assertIn(b'Tag added successfully', response.data)

    def test_search(self):
        self.test_asset_upload()
        search_query = {
            "asset_type": "model"  
        }

        
        response = self.client.get('/search/asset_type', query_string=search_query)


        self.assert200(response)

      
        data = json.loads(response.data)

    def test_search_by_asset_type(self):
        asset = Asset(type='model', filename='test_image.jpg', user_id=1)  
        db.session.add(asset)
        db.session.commit()

 
        search_query = {
            "asset_type": "model"  
         }

        response = self.client.get('/search/asset_type', query_string=search_query)

    
        self.assert200(response)

      
        data = json.loads(response.data)
        self.assertEqual(len(data['assets']), 1)  
        self.assertEqual(data['assets'][0], 'test_image.jpg') 
