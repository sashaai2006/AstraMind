const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
  res.send('Welcome to Sneak 2D API');
});

module.exports = router;