// TopBar.jsx
import React from 'react';
import { Image, Flex, Text, Divider, VStack } from '@chakra-ui/react';
import LogoImage from '../assets/pycxsim_full_logo_no_background.png'; // Update the path to the location of your image

const TopBar: React.FC = () => {
    // Replace with actual simulation data
    const simName = "Simulation Name";
    const currentStep = 5;
    const maxSteps = 100;
    const currentEpisode = 1;
    const maxEpisodes = 20;

    return (
        <Flex
            bg="#333"
            color="white"
            px="20px"
            py="10px"
            align="center"
            justify="space-between"
            h="10vh"
        >
            <Image
                src={LogoImage}
                alt="Logo"
                maxW="10%"  // Adjusted for better fit
                maxH="75%"  // Maximum height of the image
                h="auto"    // Height automatically adjusted to maintain aspect ratio
                w="auto"    // Width automatically adjusted to maintain aspect ratio
            />
            <Divider orientation="vertical" borderColor="whiteAlpha.600" mx="4" height="50%" alignSelf="center" />
            <VStack spacing={1} align="left">
                <Text fontSize="lg" fontWeight="bold">{simName}</Text>
                <Text fontSize="sm">Step: {currentStep} / {maxSteps}</Text>
                <Text fontSize="sm">Episode: {currentEpisode} / {maxEpisodes}</Text>
            </VStack>
            <Flex flex="1" /> {/* Spacer Flex to push content to the edges */}
        </Flex>
    );
};

export default TopBar;
