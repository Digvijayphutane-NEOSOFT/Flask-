# functions.py
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash

from product import app,UPLOAD_FOLDER
from database import ALLOWED_EXTENSIONS, db, cursor

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])
        created_by = 'your_user_id'  # Replace with the actual user ID or username

        # Handle file upload
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '' and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(filepath)
                photo = filename  # Save the filename/link to the database

                # Insert data into the database
                insert_query = "INSERT INTO products (name, category, price, quantity, photo, created_by) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(insert_query, (name, category, price, quantity, photo, created_by))
                db.commit()

                return redirect(url_for('index'))

    return render_template('add_product.html')

@app.route('/')
def index():
    # Assuming you want to display 10 products per page
    per_page = 10
    page = request.args.get('page', 1, type=int)  # Get the page number from the URL parameter

    # Calculate the offset to fetch the appropriate range of products
    offset = (page - 1) * per_page

    # Fetch products for the current page
    fetch_products_query = f"SELECT * FROM products LIMIT {offset}, {per_page}"
    cursor.execute(fetch_products_query)
    products = cursor.fetchall()

    return render_template('index.html', products=products, page=page)

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if request.method == 'POST':
        # Fetch existing product details
        fetch_product_query = "SELECT * FROM products WHERE id=%s"
        cursor.execute(fetch_product_query, (product_id,))
        product = cursor.fetchone()

        # Get updated values from the form
        name = request.form['name']
        category = request.form['category']
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])

        # Check if a new file is uploaded
        if 'photo' in request.files:
            photo = request.files['photo']

            # Validate and handle the file upload
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo.save(filepath)
                photo_path = filename
            else:
                # Handle invalid file types or other upload issues
                flash('Invalid file type. Please upload an image.')
                return redirect(url_for('edit_product', product_id=product_id))

        else:
            # If no new file is uploaded, retain the existing file path
            photo_path = product['photo']

        # Update the product in the database
        update_query = "UPDATE products SET name=%s, category=%s, price=%s, quantity=%s, photo=%s WHERE id=%s"
        cursor.execute(update_query, (name, category, price, quantity, photo_path, product_id))
        db.commit()

        return redirect(url_for('index'))

    # If it's a GET request, render the edit_product page
    fetch_product_query = "SELECT * FROM products WHERE id=%s"
    cursor.execute(fetch_product_query, (product_id,))
    product = cursor.fetchone()

    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    fetch_product_query = "SELECT * FROM products WHERE id=%s"
    cursor.execute(fetch_product_query, (product_id,))
    product = cursor.fetchone()

    # Delete the image file associated with the product
    if product and product['photo']:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], product['photo'])
        if os.path.exists(image_path):
            os.remove(image_path)

    delete_query = "DELETE FROM products WHERE id=%s"
    cursor.execute(delete_query, (product_id,))
    db.commit()

    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search_term']
        search_query = "SELECT * FROM products WHERE name LIKE %s"
        cursor.execute(search_query, ('%' + search_term + '%',))
        search_results = cursor.fetchall()
        return render_template('search_results.html', search_results=search_results, search_term=search_term)

    return render_template('search.html')
