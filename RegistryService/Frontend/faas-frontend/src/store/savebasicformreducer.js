// project imports
import config from '../config';

// action - state management
import * as actionTypes from './actions';

export const initialState = {
    functionName: '',
    trigger: 'Cloud Storage',
    eventType: '',
    bucketId: '',
};

// ==============================|| CUSTOMIZATION REDUCER ||============================== //

const savebasicformReducer = (state = initialState, action) => {
    let id;
    switch (action.type) {
        case actionTypes.SAVE_FORM_BASIC:
            console.log(action)
            return {
                ...state,
                ...action
            };
        default:
            return state;
    }
};

export default savebasicformReducer;
