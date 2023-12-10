// TurnAnimation.jsx
import React, { useState, useEffect } from 'react';
import { Box, Text } from '@chakra-ui/react';

const TurnAnimation = () => {
    const mockAgentNames = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Aaron'];
    const [currentAgentIndex, setCurrentAgentIndex] = useState(0);
    const [animationKey, setAnimationKey] = useState(0); // key to trigger re-render

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentAgentIndex((current) => (current + 1) % mockAgentNames.length);
            setAnimationKey(key => key + 1); // Update key to trigger re-render
        }, 2000); // Change agent every 2 seconds

        return () => clearInterval(interval);
    }, [mockAgentNames.length]);

    const getAgentNames = () => {
        const totalAgents = mockAgentNames.length;
        const nextIndex = (currentAgentIndex + 1) % totalAgents;

        return [mockAgentNames[currentAgentIndex], mockAgentNames[nextIndex]];
    };

    const [current, next] = getAgentNames();

    return (
        <Box display="flex" alignItems="center" height="50px" overflow="hidden">
            {mockAgentNames.map((name, index) => (
                <Text
                    key={index}
                    width="100px"
                    textAlign="center"
                    opacity={currentAgentIndex === index ? 1 : 0.3}
                    transition="opacity 0.5s ease-in-out"
                    animation={`fade 4s ${index * 2}s infinite`}
                    className={currentAgentIndex === index ? 'highlight' : ''}
                >
                    {name}
                </Text>
            ))}
        </Box>
    );
};

export default TurnAnimation;






