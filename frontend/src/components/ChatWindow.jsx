import React, { useState } from "react";
import Message from "./Message";
import InputBox from "./InputBox";
import { sendMessageToChatbot } from "../services/api";

const ChatWindow = () => {
    const [messages, setMessages] = useState([
        { text: "Hello! How can I assist you today?", sender: "bot" }
    ]);
    const [loading, setLoading] = useState(false); // New state for loading indicator

    const sendMessage = async (text) => {
        const newMessages = [...messages, { text, sender: "user" }];
        setMessages(newMessages);
        setLoading(true); // Show loading indicator

        try {
            const botResponse = await sendMessageToChatbot(text);
            setMessages([...newMessages, { text: botResponse, sender: "bot" }]);
        } catch (error) {
            setMessages([...newMessages, { text: "Error: Failed to get response.", sender: "bot" }]);
        }

        setLoading(false); // Hide loading indicator
    };

    return (
        <div className="chat-window">
            <div className="messages">
                {messages.map((msg, index) => (
                    <Message key={index} text={msg.text} sender={msg.sender} />
                ))}
                {loading && <div className="loading-message">🤖 Typing...</div>} {/* Loading indicator */}
            </div>
            <InputBox sendMessage={sendMessage} />
        </div>
    );
};

export default ChatWindow;
