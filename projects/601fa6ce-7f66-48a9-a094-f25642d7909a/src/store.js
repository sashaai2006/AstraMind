// store.js
import { createStore, combineReducers } from 'redux';

const initialState = {
  game: {
    player: {
      x: 0,
      y: 0,
      score: 0
    },
    obstacles: [],
    powerUps: []
  }
};

const gameReducer = (state = initialState, action) => {
  switch (action.type) {
    case 'MOVE_PLAYER':
      return {
        ...state,
        game: {
          ...state.game,
          player: {
            ...state.game.player,
            x: action.payload.x,
            y: action.payload.y
          }
        }
      };
    case 'ADD_OBSTACLE':
      return {
        ...state,
        game: {
          ...state.game,
          obstacles: [...state.game.obstacles, action.payload]
        }
      };
    case 'ADD_POWER_UP':
      return {
        ...state,
        game: {
          ...state.game,
          powerUps: [...state.game.powerUps, action.payload]
        }
      };
    default:
      return state;
  }
};

const rootReducer = combineReducers({ game: gameReducer });

const store = createStore(rootReducer);

export default store;