import { useState, useEffect } from 'react';
import axios from 'axios';

const useFetchWithInterval = <T,>(url: string, interval: number): { data: T | null; error: Error | null } => {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get<T>(url);
        setData(response.data); // Set the fetched data
      } catch (error) {
        setError(error as Error); // Set the error if the request fails
      }
    };

    fetchData(); // Fetch data immediately when the hook is used

    const intervalId = setInterval(fetchData, interval); // Set up the interval

    return () => clearInterval(intervalId); // Cleanup the interval on unmount
  }, [url, interval]); // Re-run the effect if the url or interval changes

  return { data, error }; // Return both data and error so the component can handle them
};

export default useFetchWithInterval;