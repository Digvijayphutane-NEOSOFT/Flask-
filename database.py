# database.py
import pymysql

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Connect to the database
db = pymysql.connect(port=3306, host='localhost', user='root', password='password', db='store_main', cursorclass=pymysql.cursors.DictCursor)
cursor = db.cursor()

# Create the products table if not exists
create_table_query = """
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(255),
    price FLOAT,
    quantity INT,
    photo VARCHAR(255),
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
)
"""
cursor.execute(create_table_query)
db.commit()
