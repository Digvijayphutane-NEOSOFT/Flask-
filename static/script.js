// Function to show confirmation dialog
function confirmDelete() {
    return confirm("Are you sure you want to delete this product?");
}

// Function to update the product list dynamically
function updateProductList() {
    // You may need to adjust the URL based on your Flask routes
    fetch('/products')
        .then(response => response.json())
        .then(products => {
            // Assuming you have a function to update the product table
            updateProductTable(products);
        })
        .catch(error => console.error('Error updating product list:', error));
}

// Example: Update the product table with new data
function updateProductTable(products) {
    const tableBody = document.querySelector('tbody');

    // Clear existing rows
    tableBody.innerHTML = '';

    // Iterate through the products and add rows to the table
    products.forEach(product => {
        const row = tableBody.insertRow();
        row.innerHTML = `
            <td>${product.id}</td>
            <td>${product.name}</td>
            <td>${product.category}</td>
            <td>${product.price}</td>
            <td>${product.quantity}</td>
            <td><img src="{{ url_for('static', filename='images/' + product.photo) }}" alt="{{ product.name }}"></td>
            <td>
                <a href="/edit_product/${product.id}">Edit</a>
                <a href="/delete_product/${product.id}" onclick="return confirmDelete()">Delete</a>
            </td>
        `;
    });
}

// Event listener for form submission
document.addEventListener('submit', function(event) {
    // Check if the submitted form is the add or edit product form
    if (event.target.matches('#addProductForm') || event.target.matches('#editProductForm')) {
        // Prevent the default form submission
        event.preventDefault();

        // You may need to adjust the URL based on your Flask routes
        const url = event.target.getAttribute('action');
        const method = event.target.getAttribute('method');
        const formData = new FormData(event.target);

        // Make an AJAX request to add or edit the product
        fetch(url, {
            method: method,
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Assuming you have a function to handle the response
            handleFormResponse(data);
        })
        .catch(error => console.error('Error submitting form:', error));
    }
});

// Example: Handle the form response and update the product list
function handleFormResponse(data) {
    if (data.success) {
        // Close the modal or perform any other necessary actions

        // Update the product list dynamically
        updateProductList();
    } else {
        // Handle errors or display error messages
        console.error('Form submission failed:', data.message);
    }
}
