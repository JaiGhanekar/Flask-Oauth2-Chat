import os
DATABASE_TYPE = os.environ.get('DATABASE_TYPE', 'mysql')
DATABASE_USER = os.environ.get('DATABASE_USER', 'root')
DATABASE_HOST = os.environ.get('DATABASE_HOST', 'db')
DATABASE_PASS = os.environ.get('DATABASE_PASS', 'shittypassword')
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'fakedb')
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
WHITELIST = os.environ.get('WHITELIST', 'www.youtube.com')
DATABASE_URL = '{0}://{1}:{2}@{3}/{4}'.format(DATABASE_TYPE, DATABASE_USER, DATABASE_PASS, DATABASE_HOST, DATABASE_NAME)
SECRET_KEY = 'its_a_secret'
FAKE_NAME = 'Bot'
FAKE_EMAIL = 'email@gmail.com'
FAKE_PASSWORD = 'password'