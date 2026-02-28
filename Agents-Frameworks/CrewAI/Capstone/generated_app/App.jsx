import React, { useEffect, useState } from 'react';

const App = () => {
  const [products, setProducts] = useState([]);
  const [orderId, setOrderId] = useState('');
  const [orderStatus, setOrderStatus] = useState(null);
  const [customerId, setCustomerId] = useState('123'); // Example customer ID
  const [orderProducts, setOrderProducts] = useState([{ productId: '1', quantity: 1 }]); // Example order

  useEffect(() => {
    const fetchProducts = async () => {
      const response = await fetch('http://localhost:8000/products');
      const data = await response.json();
      setProducts(data);
    };
    fetchProducts();
  }, []);

  const createOrder = async () => {
    const response = await fetch('http://localhost:8000/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ customerId, products: orderProducts }),
    });
    const data = await response.json();
    setOrderId(data.id);
  };

  const fetchOrderStatus = async () => {
    const response = await fetch(`http://localhost:8000/orders/${orderId}`);
    const data = await response.json();
    setOrderStatus(data);
  };

  return (
    <div>
      <h1>Product List</h1>
      <ul>
        {products.map(product => (
          <li key={product.id}>
            {product.name} - ${product.price}
          </li>
        ))}
      </ul>
      <button onClick={createOrder}>Create Order</button>
      {orderId && (
        <div>
          <h2>Order ID: {orderId}</h2>
          <button onClick={fetchOrderStatus}>Check Order Status</button>
          {orderStatus && (
            <div>
              <h3>Order Status: {orderStatus.status}</h3>
              <p>Total Amount: ${orderStatus.totalAmount}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default App;