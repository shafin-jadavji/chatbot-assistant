import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from logging import Logger
from routes.chat import chat_endpoint
from pydantic import BaseModel

# Mocking the logger and chat_with_memory functions
class ChatRequest(BaseModel):
    message: str

@pytest.mark.asyncio
class TestChatEndpoint:
    @pytest.fixture
    def mock_logger(self, mocker):
        return mocker.patch('routes.chat.logger')

    @pytest.fixture
    def mock_chat_with_memory(self, mocker):
        return mocker.patch('routes.chat.chat_with_memory')

    async def test_successful_chat_response(self, mock_logger, mock_chat_with_memory):
        mock_chat_with_memory.return_value = "Test response"
        request = ChatRequest(message="Hello")
        
        response = await chat_endpoint(request)
        
        assert response == {"response": "Test response"}
        mock_logger.info.assert_any_call("Received message: Hello")
        mock_logger.info.assert_any_call("OpenAI Response: Test response")

    async def test_error_handling(self, mock_logger, mock_chat_with_memory):
        mock_chat_with_memory.side_effect = Exception("Test error")
        request = ChatRequest(message="Hello")
        
        response = await chat_endpoint(request)
        
        assert response == {"error": "Internal Server Error"}
        mock_logger.error.assert_called_once()

    async def test_empty_message(self, mock_logger, mock_chat_with_memory):
        mock_chat_with_memory.return_value = ""
        request = ChatRequest(message="")
        
        response = await chat_endpoint(request)
        
        assert response == {"response": ""}
        mock_logger.info.assert_any_call("Received message: ")

    async def test_special_characters_message(self, mock_logger, mock_chat_with_memory):
        mock_chat_with_memory.return_value = "Special response"
        request = ChatRequest(message="!@#$%^&*()")
        
        response = await chat_endpoint(request)
        
        assert response == {"response": "Special response"}
        mock_logger.info.assert_any_call("Received message: !@#$%^&*()")
