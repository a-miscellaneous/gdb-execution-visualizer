export interface ExeHistory{ //maps file name to equivalent array of histories
    [key: string] : LineMapping;
}

export interface LineMapping{ //maps line number to equivalent history type
    [key: string] : LineHistory|ArgsHistory;
}

export interface LineHistoryValues{
    value: string;
    step: number;
    stackHeight: number;
}

export interface LineHistory{
    var : string;
    values : LineHistoryValues[];
}

export interface ArgsHistoryValues{
    dict : any;
    step : number;
    stackHeight : number;
}

export interface ArgsHistory{
    functionName : number;
    values : ArgsHistoryValues[];
}

export interface FileToHTML{
    [key: string] : string[];
}
