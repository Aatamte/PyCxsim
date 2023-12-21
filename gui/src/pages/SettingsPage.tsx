// SettingsPage.tsx
import React, { useState } from 'react';
import {
  Box,
  FormControl,
  FormLabel,
  Input,
  Select,
  Button,
  useColorMode,
  VStack,
} from '@chakra-ui/react';
import {useData} from "../DataProvider";
import { useNavigate } from 'react-router-dom';

type Settings = {
  colorScheme: string;
};

const SettingsPage: React.FC = () => {
  const { state } = useData();
  const [settings, setSettings] = useState<Settings>({colorScheme: 'light' });
  const { setColorMode } = useColorMode();
  const navigate = useNavigate();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSettings({ ...settings, [e.target.name]: e.target.value });
  };

  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSettings({ ...settings, [e.target.name]: e.target.value });
    if (e.target.name === 'colorScheme') {
      setColorMode(e.target.value);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Settings submitted:', settings);
    // Here you can add logic to persist these settings
  };

  return (
    <Box p={4}>
      {/* Back to Home Button */}
      <Button
        colorScheme="blue"
        onClick={() => navigate('/')}
        mb={4} // margin-bottom for spacing
      >
        Back to Home
      </Button>
      <form onSubmit={handleSubmit}>
        <VStack spacing={4} align="stretch">
          <FormControl isRequired>
            <FormLabel htmlFor='host'>Host</FormLabel>
            <Input
              id='host'
              name='host'
              type='text'
              value={state.socketParams.host}
              onChange={handleInputChange}
            />
          </FormControl>

          <FormControl isRequired>
            <FormLabel htmlFor='port'>Port</FormLabel>
            <Input
              id='port'
              name='port'
              type='number'
              value={state.socketParams.port}
              onChange={handleInputChange}
            />
          </FormControl>

          <FormControl>
            <FormLabel htmlFor='colorScheme'>Color Scheme</FormLabel>
            <Select
              id='colorScheme'
              name='colorScheme'
              value={settings.colorScheme}
              onChange={handleSelectChange}
            >
              <option value='light'>Light</option>
              <option value='dark'>Dark</option>
            </Select>
          </FormControl>

          <Button type='submit' colorScheme='blue'>
            Save Settings
          </Button>
        </VStack>
      </form>
    </Box>
  );
};

export default SettingsPage;
