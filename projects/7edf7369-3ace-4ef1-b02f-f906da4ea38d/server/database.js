const mongoose = require('mongoose');

mongoose.connect('mongodb://localhost/sneak', { useNewUrlParser: true, useUnifiedTopology: true });

const gameSchema = new mongoose.Schema({
  board: String,
  score: Number,
  player: String
});

const Game = mongoose.model('Game', gameSchema);

module.exports = { Game };