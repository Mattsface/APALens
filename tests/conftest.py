import os
from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_logger():
    """Fixture providing a mock logger"""
    return Mock()


@pytest.fixture
def sample_http_response():
    """Fixture providing a sample HTTP response"""
    response = Mock()
    response.status_code = 200
    response.reason = "OK"
    response.url = "https://api.example.com/api/v1/test"
    response.json.return_value = {"data": "test"}
    return response


@pytest.fixture
def sample_graphql_response():
    """Fixture providing a sample GraphQL response"""
    return {
        "data": {
            "generateAccessToken": {
                "accessToken": "test-token-123",
                "__typename": "AccessTokenPayload",
            }
        }
    }


@pytest.fixture
def refresh_token_env():
    """Fixture that sets and cleans up APA_REFRESH_TOKEN environment variable"""
    original_token = os.environ.get("APA_REFRESH_TOKEN")
    os.environ["APA_REFRESH_TOKEN"] = "test-refresh-token"
    yield "test-refresh-token"
    if original_token:
        os.environ["APA_REFRESH_TOKEN"] = original_token
    else:
        del os.environ["APA_REFRESH_TOKEN"]


@pytest.fixture
def http_adapter():
    """Fixture providing a basic HttpAdapter instance"""
    from src.adapters import HttpAdapter

    return HttpAdapter(hostname="test.api.com", ver="v1")


@pytest.fixture
def graphql_adapter():
    """Fixture providing a basic GraphQLAdapter instance"""
    from src.adapters import GraphQLAdapter

    return GraphQLAdapter(hostname="test.gql.com", ver="v1")
