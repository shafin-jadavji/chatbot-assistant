import React, { useState } from "react";

const InputBox = ({ sendMessage }) => {
    const [text, setText] = useState("");

    const handleSend = () => {
        if (text.trim() !== "") {
            sendMessage(text);
            setText(""); // Clear input after sending
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === "Enter") {
            handleSend();
        }
    };

    return (
        <div className="input-box">
            <input 
                type="text" 
                value={text} 
                onChange={(e) => setText(e.target.value)} 
                onKeyDown={handleKeyPress}
                placeholder="Type a message..."
            />
            <button onClick={handleSend}>Send</button>
        </div>
    );
};

export default InputBox;
