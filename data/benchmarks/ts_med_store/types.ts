// State store interfaces
export interface Action {
    type: string;
    payload?: any;
}
export interface State {
    [key: string]: any;
}
export type Reducer = (state: State, action: Action) => State;
