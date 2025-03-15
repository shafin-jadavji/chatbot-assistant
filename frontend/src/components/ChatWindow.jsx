import React, { useState } from "react";
import Message from "./Message";
import InputBox from "./InputBox";
import { sendMessageToChatbot } from "../services/api";

const ChatWindow = () => {
    const [messages, setMessages] = useState([
        { text: "Hello! How can I assist you today?", sender: "bot" }
    ]);

    const sendMessage = async (text) => {
        const newMessages = [...messages, { text, sender: "user" }];
        setMessages(newMessages);

        // Call API and update messages
        const botResponse = await sendMessageToChatbot(text);
        setMessages([...newMessages, { text: botResponse, sender: "bot" }]);
    };

    return (
        <div className="chat-window">
            <div className="messages">
                {messages.map((msg, index) => (
                    <Message key={index} text={msg.text} sender={msg.sender} />
                ))}
            </div>
            <InputBox sendMessage={sendMessage} />
        </div>
    );
};

export default ChatWindow;
