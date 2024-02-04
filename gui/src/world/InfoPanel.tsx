import React from "react";
import {useData} from "../DataProvider";
import {CircularProgress, CircularProgressLabel, Divider, Flex, HStack, IconButton, VStack, Text as CText} from "@chakra-ui/react";
import {MdPause, MdPlayArrow, MdSkipNext, MdSkipPrevious} from "react-icons/md";


type InfoPanelProps = {
    sidebarWidth: number;
};

const InfoPanel: React.FC<InfoPanelProps> = ({ sidebarWidth }) => {
    const { environment, sendData } = useData();

    const sendButtonAction = (action: string) => {
        sendData("action", action);
    };

    return (
        <Flex bg="gray" h="10vh" justifyContent="space-around" alignItems="center" px={4} boxShadow="0px 2px 4px rgba(0, 0, 0, 0.1)">
            <HStack spacing={4} align="center">
                {/* Episode Progress */}
                <VStack spacing={0}>
                    <CText fontSize="lg" fontWeight="bold">Episode</CText>
                    <CircularProgress value={(environment.currentEpisode / environment.maxEpisodes) * 100} color="green.400" thickness="12px">
                        <CircularProgressLabel>{`${environment.currentEpisode}/${environment.maxEpisodes}`}</CircularProgressLabel>
                    </CircularProgress>
                </VStack>

                {/* Step Progress */}
                <VStack spacing={0}>
                    <CText fontSize="lg" fontWeight="bold">Step</CText>
                    <CircularProgress value={((environment.currentStep + 1) / environment.maxSteps) * 100} color="blue.400" thickness="12px">
                        <CircularProgressLabel>{`${environment.currentStep + 1}/${environment.maxSteps}`}</CircularProgressLabel>
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
                <CText fontSize="md">{environment.status}</CText>
                <CText fontSize="md">Next Agent: {environment.agentQueue?.at(0)}</CText>

            </VStack>
        </Flex>
    );
};


export default InfoPanel;