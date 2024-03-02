import React from "react";
import { useData } from "../DataProvider";
import { CircularProgress, CircularProgressLabel, Divider, Flex, HStack, IconButton, VStack, Text as CText } from "@chakra-ui/react";
import { MdPause, MdPlayArrow, MdSkipNext, MdSkipPrevious } from "react-icons/md";
import useFetchWithInterval from "../useFetchWithInterval";

interface DataItem {
    key: string;
    value: string;
}

type InfoPanelProps = {
    sidebarWidth: number;
};

const InfoPanel: React.FC<InfoPanelProps> = ({ sidebarWidth }) => {
    const { sendData } = useData();
    const { data, error } = useFetchWithInterval<DataItem[]>('http://localhost:8000/tables/cxmetadata', 3000);

    const sendButtonAction = (action: string) => {
        sendData("action", action);
    };

    const findValueByKey = (key: string): string => {
        const item = data?.find(d => d.key === key);
        return item ? item.value : 'N/A';
    };

    // Example usage of findValueByKey
    const currentEpisode = findValueByKey('current_episode');
    const maxEpisodes = findValueByKey('max_episodes');
    const currentStep = findValueByKey('current_step');
    const maxSteps = findValueByKey('max_steps');
    const status = findValueByKey('current_status');
    const nextAgent = findValueByKey('next_agent');

    return (
        <Flex bg="gray" h="10vh" justifyContent="space-around" alignItems="center" px={4} boxShadow="0px 2px 4px rgba(0, 0, 0, 0.1)">
            <HStack spacing={4} align="center">
                {/* Episode Progress */}
                <VStack spacing={0}>
                    <CText fontSize="lg" fontWeight="bold">Episode</CText>
                    <CircularProgress value={parseInt(currentEpisode) / parseInt(maxEpisodes) * 100} color="green.400" thickness="12px">
                        <CircularProgressLabel>{`${currentEpisode}/${maxEpisodes}`}</CircularProgressLabel>
                    </CircularProgress>
                </VStack>

                {/* Step Progress */}
                <VStack spacing={0}>
                    <CText fontSize="lg" fontWeight="bold">Step</CText>
                    <CircularProgress value={(parseInt(currentStep) + 1) / parseInt(maxSteps) * 100} color="blue.400" thickness="12px">
                        <CircularProgressLabel>{`${parseInt(currentStep) + 1}/${maxSteps}`}</CircularProgressLabel>
                    </CircularProgress>
                </VStack>
            </HStack>

            <Divider orientation="vertical" height="5vh" />

            {/* Control Buttons */}
            <HStack spacing={2}>
                <IconButton icon={<MdSkipPrevious />} size="lg" aria-label="Last Step" onClick={() => sendButtonAction('back')} isDisabled={true}/>
                <IconButton icon={<MdPause />} size="lg" aria-label="Pause" onClick={() => sendButtonAction('pause')} />
                <IconButton icon={<MdPlayArrow />} size="lg" aria-label="Play" onClick={() => sendButtonAction('play')} isDisabled={true}/>
                <IconButton icon={<MdSkipNext />} size="lg" aria-label="Next Step" onClick={() => sendButtonAction('next')} />
            </HStack>

            <Divider orientation="vertical" height="5vh" />

            {/* Status Placeholder */}
            <VStack spacing={0} align="center">
                <CText fontSize="md">{status}</CText>
                <CText fontSize="md">Next Agent: {nextAgent}</CText>
            </VStack>
        </Flex>
    );
};

export default InfoPanel;

