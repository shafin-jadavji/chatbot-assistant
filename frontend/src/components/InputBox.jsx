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
            // If Shift key is pressed with Enter, add a new line
            if (e.shiftKey) {
                return; // Let the default behavior happen (new line)
            } else {
                // Otherwise send the message
                e.preventDefault(); // Prevent default to avoid adding a new line
                handleSend();
            }
        }
    };

    return (
        <div className="input-box">
            <textarea 
                value={text} 
                onChange={(e) => setText(e.target.value)} 
                onKeyDown={handleKeyPress}
                placeholder="Type a message... (Shift+Enter for new line)"
                rows="1"
                className="input-textarea"
            />
            <button onClick={handleSend}>Send</button>
        </div>
    );
};

export default InputBox;