import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

export const sendMessageToChatbot = async (message) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/chat`, { message });
        return response.data.response;
    } catch (error) {
        console.error("Error sending message:", error);
        return "Error: Could not get response.";
    }
};
