// Central state store
import { Action, State, Reducer } from "./types.js";

export class Store {
    private state: State;
    private reducer: Reducer;

    constructor(reducer: Reducer, initialState: State = {}) {
        this.reducer = reducer;
        this.state = initialState;
    }

    public getState(): State {
        return this.state;
    }

    public dispatch(action: Action): void {
        this.state = this.reducer(this.state, action);
    }
}
