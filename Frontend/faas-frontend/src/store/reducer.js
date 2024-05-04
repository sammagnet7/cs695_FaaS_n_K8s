import { combineReducers } from 'redux';

// reducer import
import customizationReducer from './customizationReducer';
import savebasicformReducer from './savebasicformreducer';
import savecodedepsReducer from './savecodedepsReducer';
import functionLogReducer from './functionLogReducer';
// ==============================|| COMBINE REDUCER ||============================== //

const reducer = combineReducers({
  customization: customizationReducer,
  basicform: savebasicformReducer,
  code: savecodedepsReducer,
  log: functionLogReducer,
});

export default reducer;
