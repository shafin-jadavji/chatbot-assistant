import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from logging import Logger
from routes.chat import chat_endpoint
from pydantic import BaseModel
from fastapi import Request

# Mocking the logger and chat_with_memory functions
class ChatRequest(BaseModel):
    message: str
    test_ip: str = None

@pytest.mark.asyncio
class TestChatEndpoint:
    @pytest.fixture
    def mock_logger(self, mocker):
        return mocker.patch('routes.chat.logger')

    @pytest.fixture
    def mock_chat_with_memory(self, mocker):
        return mocker.patch('routes.chat.chat_with_memory')
        
    @pytest.fixture
    def mock_request(self, mocker):
        mock_req = mocker.MagicMock()
        mock_req.client.host = "127.0.0.1"
        return mock_req

    async def test_successful_chat_response(self, mock_logger, mock_chat_with_memory, mock_request):
        mock_chat_with_memory.return_value = "Test response"
        request = ChatRequest(message="Hello")
        
        response = await chat_endpoint(request, mock_request)
        
        assert response == {"response": "Test response"}
        mock_logger.info.assert_any_call("Received message: Hello")
        mock_logger.info.assert_any_call("OpenAI Response: Test response")
        mock_chat_with_memory.assert_called_once_with("Hello", client_ip="127.0.0.1")

    async def test_error_handling(self, mock_logger, mock_chat_with_memory, mock_request):
        mock_chat_with_memory.side_effect = Exception("Test error")
        request = ChatRequest(message="Hello")
        
        response = await chat_endpoint(request, mock_request)
        
        assert response == {"error": "Internal Server Error"}
        mock_logger.error.assert_called_once()

    async def test_empty_message(self, mock_logger, mock_chat_with_memory, mock_request):
        mock_chat_with_memory.return_value = ""
        request = ChatRequest(message="")
        
        response = await chat_endpoint(request, mock_request)
        
        assert response == {"response": ""}
        mock_logger.info.assert_any_call("Received message: ")
        mock_chat_with_memory.assert_called_once_with("", client_ip="127.0.0.1")

    async def test_special_characters_message(self, mock_logger, mock_chat_with_memory, mock_request):
        mock_chat_with_memory.return_value = "Special response"
        request = ChatRequest(message="!@#$%^&*()")
        
        response = await chat_endpoint(request, mock_request)
        
        assert response == {"response": "Special response"}
        mock_logger.info.assert_any_call("Received message: !@#$%^&*()")
        mock_chat_with_memory.assert_called_once_with("!@#$%^&*()", client_ip="127.0.0.1")
        
    async def test_with_test_ip_override(self, mock_logger, mock_chat_with_memory, mock_request):
        mock_chat_with_memory.return_value = "Test response with custom IP"
        request = ChatRequest(message="Hello", test_ip="192.168.1.100")
        
        response = await chat_endpoint(request, mock_request)
        
        assert response == {"response": "Test response with custom IP"}
        mock_chat_with_memory.assert_called_once_with("Hello", client_ip="192.168.1.100")
        mock_logger.debug.assert_called_once_with("Using IP: 192.168.1.100")