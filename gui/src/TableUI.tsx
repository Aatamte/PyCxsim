import React from 'react';
import {
    Table,
    Thead,
    Tbody,
    Tr,
    Th,
    Td,
    TableContainer,
    Box,
    Text,
    useColorMode,
} from '@chakra-ui/react';

interface TableProps {
  data: Record<string, any>[];
}

const ChakraTable: React.FC<TableProps> = ({ data }) => {
    const { colorMode } = useColorMode();

  if (!data || data.length === 0) {
    return (
      <Box>
        <Text>No data available.</Text>
      </Box>
    );
  }
  const headers = Object.keys(data[0]);

  return (
    <TableContainer>
      <Table variant="simple">
        <Thead>
          <Tr>
            {headers.map((header, index) => (
              <Th key={index} color={"white"}>{header}</Th>
            ))}
          </Tr>
        </Thead>
            <Tbody>
              {data.map((row, rowIndex) => (
                <Tr key={rowIndex}>
                  {headers.map((header, cellIndex) => (
                    <Td key={cellIndex} fontSize={12}>
                      {typeof row[header] === 'object'
                        ? JSON.stringify(row[header])
                        : row[header]}
                    </Td>
                  ))}
                </Tr>
              ))}
            </Tbody>
      </Table>
    </TableContainer>
  );
};

export default ChakraTable;