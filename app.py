# app.py
import logging
from flask import render_template, request
from product_operation import add_product, index, edit_product, delete_product, search
from product import app

# Configure the logger
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)-8s %(message)s', 
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='app.log',
                    filemode='w')
# Log a message
logging.debug('Starting the Flask application...')

if __name__ == '__main__':
    app.run(debug=True)
