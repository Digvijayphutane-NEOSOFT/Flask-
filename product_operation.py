'''# functions.py
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash

from product import app, UPLOAD_FOLDER
from database import ALLOWED_EXTENSIONS, db, cursor

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    try:
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
                else:
                    flash('Invalid file type. Please upload an image.')
            else:
                flash('No image file provided.')

    except Exception as e:
        flash(f"An error occurred: {str(e)}")

    return render_template('add_product.html')

@app.route('/')
def index():
    try:
        # Assuming you want to display 5 products per page
        per_page = 5
        page = request.args.get('page', 1, type=int)  # Get the page number from the URL parameter

        # Calculate the offset to fetch the appropriate range of products
        offset = (page - 1) * per_page

        # Fetch products for the current page, ordered by id in descending order
        fetch_products_query = f"SELECT * FROM products ORDER BY id DESC LIMIT {offset}, {per_page}"
        cursor.execute(fetch_products_query)
        products = cursor.fetchall()

        # Count total number of products
        count_query = "SELECT COUNT(*) FROM products"
        cursor.execute(count_query)
        total_products = cursor.fetchone()['COUNT(*)']

        # Calculate the total number of pages
        total_pages = (total_products + per_page - 1) // per_page

        return render_template('index.html', products=products, page=page, total_pages=total_pages)

    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        return render_template('error.html')  # Create an error.html template for displaying errors

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    try:
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

    except Exception as e:
        flash(f"An error occurred: {str(e)}")

    # If it's a GET request, render the edit_product page
    fetch_product_query = "SELECT * FROM products WHERE id=%s"
    cursor.execute(fetch_product_query, (product_id,))
    product = cursor.fetchone()

    return render_template('edit_product.html', product=product)

# @app.route('/delete_product/<int:product_id>')
# def delete_product(product_id):
#     try:
#         fetch_product_query = "SELECT * FROM products WHERE id=%s"
#         cursor.execute(fetch_product_query, (product_id,))
#         product = cursor.fetchone()

#         # Delete the image file associated with the product
#         if product and product['photo']:
#             image_path = os.path.join(app.config['UPLOAD_FOLDER'], product['photo'])
#             if os.path.exists(image_path):
#                 os.remove(image_path)

#         delete_query = "DELETE FROM products WHERE id=%s"
#         cursor.execute(delete_query, (product_id,))
#         db.commit()

#         return redirect(url_for('index'))

#     except Exception as e:
#         flash(f"An error occurred: {str(e)}")

#     return render_template('error.html')  # Create an error.html template for displaying errors
@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    try:
        fetch_product_query = "SELECT * FROM products WHERE id=%s"
        cursor.execute(fetch_product_query, (product_id,))
        product = cursor.fetchone()

        if product:
            # Get the image file path
            image_filename = product['photo']
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'images', image_filename)

            # Check if the image file exists, then delete it
            if os.path.exists(image_path):
                os.remove(image_path)
                flash(f"Image file '{image_filename}' deleted successfully", 'success')
            else:
                flash(f"Image file '{image_filename}' not found", 'error')

            # Delete the product from the database
            delete_query = "DELETE FROM products WHERE id=%s"
            cursor.execute(delete_query, (product_id,))
            db.commit()

            flash('Product deleted successfully', 'success')
        else:
            flash(f"Product with ID {product_id} not found", 'error')

        return redirect(url_for('index'))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'error')

    return render_template('error.html')
@app.route('/search', methods=['GET', 'POST'])
def search():
    try:
        if request.method == 'POST':
            search_term = request.form['search_term']
            search_query = "SELECT * FROM products WHERE name LIKE %s"
            cursor.execute(search_query, ('%' + search_term + '%',))
            search_results = cursor.fetchall()
            return render_template('search_results.html', search_results=search_results, search_term=search_term)

    except Exception as e:
        flash(f"An error occurred: {str(e)}")

    return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=True)
'''
import os
import logging
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash

from product import app, UPLOAD_FOLDER,logger
from database import ALLOWED_EXTENSIONS, db, cursor

# Configure the logger
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('functions.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    try:
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

                    logger.debug(f'Added product: {name}')

                    return redirect(url_for('index'))
                else:
                    flash('Invalid file type. Please upload an image.')
            else:
                flash('No image file provided.')

    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        logger.error(f'Error adding product: {str(e)}')

    return render_template('add_product.html')

@app.route('/')
def index():
    try:
        # Assuming you want to display 5 products per page
        per_page = 5
        page = request.args.get('page', 1, type=int)  # Get the page number from the URL parameter

        # Calculate the offset to fetch the appropriate range of products
        offset = (page - 1) * per_page

        # Fetch products for the current page, ordered by id in descending order
        fetch_products_query = f"SELECT * FROM products ORDER BY id DESC LIMIT {offset}, {per_page}"
        cursor.execute(fetch_products_query)
        products = cursor.fetchall()

        # Count total number of products
        count_query = "SELECT COUNT(*) FROM products"
        cursor.execute(count_query)
        total_products = cursor.fetchone()['COUNT(*)']

        # Calculate the total number of pages
        total_pages = (total_products + per_page - 1) // per_page

        logger.debug(f'Fetched {len(products)} products for page {page}')

        return render_template('index.html', products=products, page=page, total_pages=total_pages)

    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        logger.error(f'Error fetching products: {str(e)}')
        return render_template('error.html')  # Create an error.html template for displaying errors

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    try:
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
                    flash('Invalid file type. Please upload an image.')
                    return redirect(url_for('edit_product', product_id=product_id))

            else:
                # If no new file is uploaded, retain the existing file path
                photo_path = product['photo']

            # Update the product in the database
            update_query = "UPDATE products SET name=%s, category=%s, price=%s, quantity=%s, photo=%s WHERE id=%s"
            cursor.execute(update_query, (name, category, price, quantity, photo_path, product_id))
            db.commit()

            logger.debug(f'Updated product: {name}')

            return redirect(url_for('index'))

    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        logger.error(f'Error updating product: {str(e)}')

    # If it's a GET request, render the edit_product page
    fetch_product_query = "SELECT * FROM products WHERE id=%s"
    cursor.execute(fetch_product_query, (product_id,))
    product = cursor.fetchone()

    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    try:
        fetch_product_query = "SELECT * FROM products WHERE id=%s"
        cursor.execute(fetch_product_query, (product_id,))
        product = cursor.fetchone()

        if product:
            # Get the image file path
            image_filename = product['photo']
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'images', image_filename)

            # Check if the image file exists, then delete it
            if os.path.exists(image_path):
                os.remove(image_path)
                flash(f"Image file '{image_filename}' deleted successfully", 'success')
            else:
                flash(f"Image file '{image_filename}' not found", 'error')

            # Delete the product from the database
            delete_query = "DELETE FROM products WHERE id=%s"
            cursor.execute(delete_query, (product_id,))
            db.commit()

            logger.debug(f'Deleted product: {product["name"]}')

            flash('Product deleted successfully', 'success')
        else:
            flash(f"Product with ID {product_id} not found", 'error')

        return redirect(url_for('index'))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'error')
        logger.error(f'Error deleting product: {str(e)}')

    return render_template('error.html')
@app.route('/search', methods=['GET', 'POST'])
def search():
    try:
        if request.method == 'POST':
            search_term = request.form['search_term']
            search_query = "SELECT * FROM products WHERE name LIKE %s"
            cursor.execute(search_query, ('%' + search_term + '%',))
            search_results = cursor.fetchall()
            return render_template('search_results.html', search_results=search_results, search_term=search_term)

        logger.debug(f'Searched for: {request.form["search_term"]}')

    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        logger.error(f'Error searching: {str(e)}')

    return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=True)