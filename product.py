# product.py
from flask import Flask
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = '12345'

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
