const express = require('express');
const router = express.Router();

router.get('/products', (req, res) => {
  res.json([{ id: 1, name: 'Product 1', price: 9.99 }, { id: 2, name: 'Product 2', price: 19.99 }]);
});

module.exports = router;