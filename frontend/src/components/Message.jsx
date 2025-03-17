import React from "react";

const Message = ({ text, sender }) => {
    // Convert newlines to <br> tags for proper display
    const formattedText = text.split('\n').map((line, i) => (
        <React.Fragment key={i}>
            {line}
            {i < text.split('\n').length - 1 && <br />}
        </React.Fragment>
    ));

    return (
        <div className={`message ${sender === "user" ? "user-message" : "bot-message"}`}>
            {formattedText}
        </div>
    );
};

export default Message;
