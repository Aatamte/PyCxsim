import React, { createContext, useContext, useState, ReactNode } from 'react';



class dataStore {

}

const data = new dataStore()


// Define the shape of your context data
interface DataContextType {
    data: any; // Replace 'any' with a more specific type as needed
    updateData: (newData: any) => void; // Replace 'any' with the type of newData
}

// Create a Context with an initial default value
const DataContext = createContext<DataContextType>({ data: {}, updateData: () => {} });

// Define the type for the props of DataProvider
interface DataProviderProps {
    children: ReactNode;
}

// Provider component
export const EnvironmentProvider: React.FC<DataProviderProps> = ({ children }) => {
    const [data, setData] = useState<Record<string, any>>({}); // Replace 'any' with more specific type as needed

    const updateData = (newData: Record<string, any>) => { // Replace 'any' with the type of newData
        setData(prevData => ({ ...prevData, ...newData }));
    };

    return (
        <DataContext.Provider value={{ data, updateData }}>
            {children}
        </DataContext.Provider>
    );
};

// Custom hook to use the data context
export const useData = (): DataContextType => useContext(DataContext);
