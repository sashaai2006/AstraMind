const express = require('express');
const app = express();
app.use(express.json());
app.get('/', (req, res) => {
  res.send('Welcome to Sneak 2D!');
});
const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});