const { Pool } = require('pg');

const dbConfig = {
  user: 'your_username',
  host: 'your_host',
  database: 'your_database',
  password: 'your_password',
  port: 5432,
};

const pool = new Pool(dbConfig);

module.exports = { pool };