// project imports
import config from '../config';

// action - state management
import * as actionTypes from './actions';

export const initialState = {
    code: '',
    deps: '',
    runtime: 'python'
};

// ==============================|| CUSTOMIZATION REDUCER ||============================== //

const savecodedepsReducer = (state = initialState, action) => {
    let id;
    switch (action.type) {
        case actionTypes.SAVE_CODE_DEPS:
            console.log("REDUCER")
            console.log(action)
            return {
                ...state,
                code: action.code,
                deps: action.deps,
                runtime: action.runtime
            };
        default:
            return state;
    }
};

export default savecodedepsReducer;