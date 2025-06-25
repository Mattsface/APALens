import pytest

from src.exceptions import HttpAdapterException


class TestHttpAdapterException:
    """Test cases for HttpAdapterException"""

    def test_http_adapter_exception_initialization(self):
        """Test HttpAdapterException initialization"""
        message = "Test error message"
        exception = HttpAdapterException(message)

        assert exception.message == message
        assert str(exception) == message

    def test_http_adapter_exception_inheritance(self):
        """Test that HttpAdapterException inherits from Exception"""
        exception = HttpAdapterException("test")
        assert isinstance(exception, Exception)

    def test_http_adapter_exception_with_empty_message(self):
        """Test HttpAdapterException with empty message"""
        exception = HttpAdapterException("")
        assert exception.message == ""
        assert str(exception) == ""

    def test_http_adapter_exception_raising(self):
        """Test raising HttpAdapterException"""
        with pytest.raises(HttpAdapterException) as exc_info:
            raise HttpAdapterException("Test error")

        assert str(exc_info.value) == "Test error"
        assert exc_info.value.message == "Test error"
