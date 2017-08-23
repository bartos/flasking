import os
import tempfile
import app
import unittest
import json

class BasicTestCase(unittest.TestCase):
    def test_index(self):
        """initial test to check if setup is ok"""
        tester = app.app.test_client(self)
        responce = tester.get('/',content_type="html/text")
        self.assertEqual(responce.status_code, 200)
        # self.assertEqual(responce.data, b'Hello, World!')
        # self.assertEqual(responce.status_code, 404)

    def test_database(self):
        """test database file esists"""
        tester = os.path.exists('tasker.db')
        self.assertTrue(tester)


class TaskerTestCase(unittest.TestCase):
    def setUp(self):
        """ clear database before each test """
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()
        app.create_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])

    def login(self, username, password):
        return self.app.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)    

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    #asserts:

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No entries yet. Add some!' in rv.data

    def test_login_logout(self):
        rv = self.login(
            app.app.config['USERNAME'],
            app.app.config['PASSWORD']
        )

        assert b'you were logged in' in rv.data

        rv = self.logout()
        assert b'you were logged out' in rv.data

        rv = self.login(
            app.app.config['USERNAME'],
            'bad_password'
        )
        
        assert b'wrong password' in rv.data

        rv = self.login(
            'badLogin',
            app.app.config['PASSWORD']
        )
        
        assert b'wrong username' in rv.data


    def test_messages(self):
        """test if user can post messgaes"""
        self.login(
            app.app.config['USERNAME'],
            app.app.config['PASSWORD']
        )
        rv = self.app.post('/add',data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        
        assert not b'No entries yet. Add some!' in rv.data
        assert b'New entry was successfully posted' in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data

    def test_delete_message(self):
        """Ensure the messages are being deleted"""
        rv = self.app.get('/delete/1')
        self.assertEqual(rv.status_code, 401)

        self.login(
            app.app.config['USERNAME'],
            app.app.config['PASSWORD']
        )

        rv = self.app.get('/delete/1')
        

        data = json.loads((rv.data).decode('utf-8'))
        print("Data: %s" %data)
        self.assertEqual(data['status'], 1)


if __name__=='__main__':
    unittest.main()