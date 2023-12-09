// Types.ts
export interface DataFrameRow {
    [key: string]: any;
}

export interface DataFrame {
    columns: string[];
    rows: DataFrameRow[];
}