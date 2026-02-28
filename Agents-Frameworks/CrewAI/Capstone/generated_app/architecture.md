```markdown
# Ecommerce System Design

## Data Model

### Product Schema
```json
{
  "id": "string",          // Unique identifier for the product
  "name": "string",        // Name of the product
  "description": "string", // Description of the product
  "price": "number",       // Price of the product
  "stock": "number",       // Available stock quantity
  "category": "string"     // Category of the product
}
```

### Order Schema
```json
{
  "id": "string",                  // Unique identifier for the order
  "customerId": "string",          // Unique identifier for the customer
  "products": [                     // List of products in the order
    {
      "productId": "string",       // Unique identifier for the product
      "quantity": "number"         // Quantity of the product ordered
    }
  ],
  "totalAmount": "number",         // Total amount for the order
  "status": "string",              // Status of the order (e.g., 'pending', 'completed')
  "createdAt": "string"            // Timestamp of order creation
}
```

## API Endpoints

### Catalog Endpoints

- **GET /api/products**
  - **Request:** No parameters
  - **Response:**
    ```json
    [
      {
        "id": "1",
        "name": "Product A",
        "description": "Description of Product A",
        "price": 29.99,
        "stock": 100,
        "category": "Electronics"
      },
      ...
    ]
    ```

- **POST /api/products**
  - **Request:**
    ```json
    {
      "name": "Product B",
      "description": "Description of Product B",
      "price": 49.99,
      "stock": 50,
      "category": "Home"
    }
    ```
  - **Response:**
    ```json
    {
      "id": "2",
      "name": "Product B",
      "description": "Description of Product B",
      "price": 49.99,
      "stock": 50,
      "category": "Home"
    }
    ```

### Order Endpoints

- **POST /api/orders**
  - **Request:**
    ```json
    {
      "customerId": "123",
      "products": [
        {
          "productId": "1",
          "quantity": 2
        }
      ]
    }
    ```
  - **Response:**
    ```json
    {
      "id": "order_1",
      "customerId": "123",
      "products": [
        {
          "productId": "1",
          "quantity": 2
        }
      ],
      "totalAmount": 59.98,
      "status": "pending",
      "createdAt": "2023-10-01T12:00:00Z"
    }
    ```

- **GET /api/orders/{id}**
  - **Request:** Path parameter `id`
  - **Response:**
    ```json
    {
      "id": "order_1",
      "customerId": "123",
      "products": [
        {
          "productId": "1",
          "quantity": 2
        }
      ],
      "totalAmount": 59.98,
      "status": "pending",
      "createdAt": "2023-10-01T12:00:00Z"
    }
    ```

## UI Screens

- **Product Listing Screen**
  - Displays a list of products with options to filter by category and sort by price.
  
- **Product Detail Screen**
  - Displays detailed information about a selected product, including an "Add to Cart" button.

- **Shopping Cart Screen**
  - Displays products added to the cart with options to adjust quantities or remove items.

- **Checkout Screen**
  - Collects customer information and displays order summary before finalizing the purchase.

- **Order Confirmation Screen**
  - Displays confirmation of the order with order details and estimated delivery time.

## Example Payloads

### Product Example
```json
{
  "id": "1",
  "name": "Product A",
  "description": "Description of Product A",
  "price": 29.99,
  "stock": 100,
  "category": "Electronics"
}
```

### Order Example
```json
{
  "id": "order_1",
  "customerId": "123",
  "products": [
    {
      "productId": "1",
      "quantity": 2
    }
  ],
  "totalAmount": 59.98,
  "status": "pending",
  "createdAt": "2023-10-01T12:00:00Z"
}
```
```