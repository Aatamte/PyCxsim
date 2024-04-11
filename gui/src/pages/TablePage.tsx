import React, { useState, useEffect } from "react";
import TableUI from "../TableUI";
import useWebSocketListener from "../sockets/useWebSocketListener";
import useFullWebSocketListener from "../sockets/useFullWebSocketListener";
import { Select } from "@chakra-ui/react";

const TablePage: React.FC = () => {
    const { data: masterData } = useWebSocketListener<any[]>('sqlite_master');
    const { data: fullData } = useFullWebSocketListener<any[]>();

    const [selectedTable, setSelectedTable] = useState<string | undefined>(undefined);
    const [tableOptions, setTableOptions] = useState<string[]>([]);

    useEffect(() => {
        if (masterData && Array.isArray(masterData)) {
            const options = masterData
                .filter(tableObject => tableObject.type === 'table')
                .map(tableObject => tableObject.name);
            setTableOptions(options);
        }
    }, [masterData]);

    // Conditional rendering logic for TableUI's data prop
    const tableData = selectedTable !== undefined ? fullData[selectedTable] || [] : [];

    return (
        <>
            <Select
                placeholder="Select Table"
                value={selectedTable}
                color="black"
                onChange={e => setSelectedTable(e.target.value)}
            >
                {tableOptions.map((table, index) => (
                    <option key={index} value={table}>{table}</option>
                ))}
            </Select>
            <TableUI data={tableData}></TableUI>
        </>
    );
}

export default TablePage;