import { ADD_FUNCTION, UPDATE_FUNCTION } from "./actions";

const initialState = {
    functions: [],
};

const functionLogReducer = (state = initialState, action) => {
    switch (action.type) {
        case ADD_FUNCTION:
            return {
                ...state,
                functions: [...state.functions, action.payload],
            };
        case UPDATE_FUNCTION:
            return {
                ...state,
                functions: state.functions.map((func) =>
                    func.id === action.payload.functionId ? { ...func, ...action.payload.updatedFunctionData } : func
                ),
            };
        default:
            return state;
    }
};

export default functionLogReducer;