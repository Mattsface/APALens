import os
from typing import Any
from unittest.mock import Mock, patch

import pytest

from src.adapters import GraphQLAdapter, HttpAdapter, HttpResult
from src.exceptions import HttpAdapterException


class TestHttpResult:
    """Test cases for HttpResult class"""

    def test_http_result_initialization(self):
        """Test HttpResult initialization with basic data"""
        result = HttpResult(200, "OK", {"key": "value"})
        assert result.status_code == 200
        assert result.message == "OK"
        assert result.data == {"key": "value"}

    def test_http_result_status_code_conversion(self):
        """Test that status_code is converted to int"""
        result = HttpResult("200", "OK", {})
        assert result.status_code == 200
        assert isinstance(result.status_code, int)

    def test_http_result_message_conversion(self):
        """Test that message is converted to string"""
        result = HttpResult(200, 123, {})
        assert result.message == "123"
        assert isinstance(result.message, str)


class TestHttpAdapter:
    """Test cases for HttpAdapter class"""

    def test_http_adapter_initialization(self):
        """Test HttpAdapter initialization with default values"""
        adapter = HttpAdapter()
        assert adapter.url == "https://api.example.com/"
        assert adapter._logger is not None

    def test_http_adapter_initialization_with_base_url_and_ver(self):
        """Test HttpAdapter initialization with base_url and ver"""
        adapter = HttpAdapter(
            hostname="custom.api.com",
            base_url="api",
            ver="v2",
        )
        assert adapter.url == "https://custom.api.com/api/v2/"

    def test_http_adapter_initialization_with_base_url(self):
        """Test HttpAdapter initialization with base_url"""
        adapter = HttpAdapter(
            hostname="custom.api.com",
            base_url="api",
        )
        assert adapter.url == "https://custom.api.com/api/"

    def test_http_adapter_initialization_with_ver(self):
        """Test HttpAdapter initialization with ver"""
        adapter = HttpAdapter(
            hostname="custom.api.com",
            ver="v2",
        )
        assert adapter.url == "https://custom.api.com/v2/"

    def test_http_adapter_initialization_with_hostname(self):
        """Test HttpAdapter initialization with hostname"""
        adapter = HttpAdapter(
            hostname="custom.api.com",
        )
        assert adapter.url == "https://custom.api.com/"

    def test_http_adapter_initialization_with_custom_logger(self):
        """Test HttpAdapter initialization with custom logger"""
        custom_logger = Mock()
        adapter = HttpAdapter(logger=custom_logger)
        assert adapter._logger == custom_logger

    @patch("src.adapters.requests.get")
    def test_http_adapter_get_success(self, mock_get: Any):
        """Test successful GET request"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.url = "https://api.example.com/api/v1/test"
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response

        adapter = HttpAdapter()
        result = adapter.get("test")

        assert result.status_code == 200
        assert result.message == "OK"
        assert result.data == {"data": "test"}
        mock_get.assert_called_once()

    @patch("src.adapters.requests.get")
    def test_http_adapter_get_with_params(self, mock_get: Any):
        """Test GET request with parameters"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.url = "https://api.example.com/test"
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response

        adapter = HttpAdapter()
        params = {"key": "value"}
        result = adapter.get("test", ep_params=params)

        assert result.status_code == 200
        assert result.message == "OK"
        assert result.data == {"data": "test"}

        mock_get.assert_called_once_with(
            url="https://api.example.com/test", params=params
        )

    @patch("src.adapters.requests.get")
    def test_http_adapter_get_404_error(self, mock_get: Any):
        """Test GET request with 404 error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.reason = "Not Found"
        mock_response.url = "https://api.example.com/api/v1/test"
        mock_response.json.return_value = {"error": "Not found"}
        mock_get.return_value = mock_response

        adapter = HttpAdapter()
        result = adapter.get("test")

        assert result.status_code == 404
        assert result.message == "Not Found"
        assert result.data == {}

    @patch("src.adapters.requests.get")
    def test_http_adapter_get_500_error(self, mock_get: Any):
        """Test GET request with 500 error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.reason = "Internal Server Error"
        mock_response.url = "https://api.example.com/api/v1/test"
        mock_get.return_value = mock_response

        adapter = HttpAdapter()
        with pytest.raises(HttpAdapterException) as exc_info:
            adapter.get("test")
        assert "500: Internal Server Error" in str(exc_info.value)

    @patch("src.adapters.requests.get")
    def test_http_adapter_get_request_exception(self, mock_get: Any):
        """Test GET request with network exception"""
        mock_get.side_effect = HttpAdapterException("Request failed")

        adapter = HttpAdapter()
        with pytest.raises(HttpAdapterException) as exc_info:
            adapter.get("test")
        assert "Request failed" in str(exc_info.value)

    @patch("src.adapters.requests.get")
    def test_http_adapter_get_json_decode_error(self, mock_get: Any):
        """Test GET request with JSON decode error"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        adapter = HttpAdapter()
        with pytest.raises(HttpAdapterException) as exc_info:
            adapter.get("test")
        assert "Bad JSON in response" in str(exc_info.value)

    @patch("src.adapters.requests.post")
    def test_http_adapter_post_success(self, mock_post: Any):
        """Test successful POST request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.url = "https://api.example.com/test"
        mock_response.json.return_value = {"data": "test"}
        mock_post.return_value = mock_response

        adapter = HttpAdapter()
        data = {"key": "value"}
        result = adapter.post("test", data=data)

        assert result.status_code == 200
        assert result.message == "OK"
        assert result.data == {"data": "test"}
        mock_post.assert_called_once_with(
            url="https://api.example.com/test", params=None, json=data
        )


class TestGraphQLAdapter:
    """Test cases for GraphQLAdapter class"""

    def test_graphql_adapter_initialization(self):
        """Test GraphQLAdapter initialization with default values"""
        adapter = GraphQLAdapter()
        assert adapter._logger is not None
        assert isinstance(adapter.http_adapter, HttpAdapter)
        assert adapter.http_adapter.url == "https://gql.poolplayers.com/"

    def test_graphql_adapter_initialization_with_ver(self):
        """Test GraphQLAdapter initialization with custom values"""
        adapter = GraphQLAdapter(hostname="custom.gql.com", ver="v2", protocol="http")
        assert adapter.http_adapter.url == "http://custom.gql.com/v2/"

    def test_graphql_adapter_initialization_with_base_url(self):
        """Test GraphQLAdapter initialization with base_url"""
        adapter = GraphQLAdapter(
            hostname="custom.gql.com",
            base_url="api",
        )
        assert adapter.http_adapter.url == "https://custom.gql.com/api/"

    def test_graphql_adapter_initialization_with_hostname(self):
        """Test GraphQLAdapter initialization with hostname"""
        adapter = GraphQLAdapter(
            hostname="custom.gql.com",
        )
        assert adapter.http_adapter.url == "https://custom.gql.com/"

    @patch.object(HttpAdapter, "post")
    def test_graphql_adapter_query(self, mock_post: Any):
        """Test GraphQL query execution"""
        # Mock HttpResult response
        mock_result = HttpResult(200, "OK", {"data": {"teams": []}})
        mock_post.return_value = mock_result

        adapter = GraphQLAdapter()
        query = "query { teams { id name } }"
        result = adapter.query(query)

        assert result.status_code == 200
        assert result.data == {"data": {"teams": []}}

        # Verify the correct payload was sent
        mock_post.assert_called_once_with(
            endpoint="graphql", data={"query": query, "variables": {}}
        )

    @patch.object(HttpAdapter, "post")
    def test_graphql_adapter_query_with_variables(self, mock_post: Any):
        """Test GraphQL query with variables"""
        mock_result = HttpResult(200, "OK", {"data": {"teams": []}})
        mock_post.return_value = mock_result

        adapter = GraphQLAdapter()
        query = "query GetTeams($league: String!) { teams(league: $league) { id } }"
        variables = {"league": "APA"}
        result = adapter.query(query, variables=variables)

        assert result.status_code == 200
        assert result.data == {"data": {"teams": []}}

        mock_post.assert_called_once_with(
            endpoint="graphql", data={"query": query, "variables": variables}
        )

    @patch.object(HttpAdapter, "post")
    def test_graphql_adapter_query_with_operation_name(self, mock_post: Any):
        """Test GraphQL query with operation name"""
        mock_result = HttpResult(200, "OK", {"data": {"teams": []}})
        mock_post.return_value = mock_result

        adapter = GraphQLAdapter()
        query = "query GetTeams { teams { id } }"
        result = adapter.query(query, operation_name="GetTeams")

        assert result.status_code == 200
        assert result.data == {"data": {"teams": []}}

        mock_post.assert_called_once_with(
            endpoint="graphql",
            data={"query": query, "variables": {}, "operationName": "GetTeams"},
        )

    @patch.object(HttpAdapter, "post")
    def test_graphql_adapter_mutation(self, mock_post: Any):
        """Test GraphQL mutation execution"""
        mock_result = HttpResult(200, "OK", {"data": {"updateTeam": {"id": "123"}}})
        mock_post.return_value = mock_result

        adapter = GraphQLAdapter()
        mutation = "mutation UpdateTeam($id: ID!) { updateTeam(id: $id) { id } }"
        variables = {"id": "123"}
        result = adapter.mutation(mutation, variables=variables)

        assert result.status_code == 200
        mock_post.assert_called_once_with(
            endpoint="graphql", data={"query": mutation, "variables": variables}
        )

    @patch.object(HttpAdapter, "post")
    def test_graphql_adapter_mutation_with_operation_name(self, mock_post: Any):
        """Test GraphQL mutation with operation name"""
        mock_result = HttpResult(200, "OK", {"data": {"updateTeam": {"id": "123"}}})
        mock_post.return_value = mock_result

        adapter = GraphQLAdapter()
        mutation = "mutation UpdateTeam($id: ID!) { updateTeam(id: $id) { id } }"
        result = adapter.mutation(mutation, operation_name="UpdateTeam")

        assert result.status_code == 200
        assert result.data == {"data": {"updateTeam": {"id": "123"}}}

        mock_post.assert_called_once_with(
            endpoint="graphql",
            data={"query": mutation, "variables": {}, "operationName": "UpdateTeam"},
        )

    @patch.object(HttpAdapter, "post")
    def test_graphql_adapter_generate_access_token_success(self, mock_post: Any):
        """Test successful access token generation"""
        mock_result = HttpResult(
            200,
            "OK",
            {
                "data": {
                    "generateAccessToken": {
                        "accessToken": "test-token-123",
                        "__typename": "AccessTokenPayload",
                    }
                }
            },
        )
        mock_post.return_value = mock_result

        adapter = GraphQLAdapter()
        token = adapter.generate_access_token(refresh_token="refresh-token-123")

        assert token == "test-token-123"
        mock_post.assert_called_once()

    @patch.object(HttpAdapter, "post")
    def test_graphql_adapter_generate_access_token_with_env_var(self, mock_post: Any):
        """Test access token generation using environment variable"""
        mock_result = HttpResult(
            200,
            "OK",
            {
                "data": {
                    "generateAccessToken": {
                        "accessToken": "test-token-123",
                        "__typename": "AccessTokenPayload",
                    }
                }
            },
        )
        mock_post.return_value = mock_result

        # Set environment variable
        os.environ["APA_REFRESH_TOKEN"] = "env-refresh-token"

        adapter = GraphQLAdapter()
        token = adapter.generate_access_token()

        assert token == "test-token-123"
        mock_post.assert_called_once()

        # Clean up
        del os.environ["APA_REFRESH_TOKEN"]

    def test_graphql_adapter_generate_access_token_no_refresh_token(self):
        """Test access token generation without refresh token"""
        adapter = GraphQLAdapter()

        with pytest.raises(HttpAdapterException) as exc_info:
            adapter.generate_access_token()
        assert "No refresh token provided" in str(exc_info.value)

    @patch.object(HttpAdapter, "post")
    def test_graphql_adapter_generate_access_token_http_error(self, mock_post: Any):
        """Test access token generation with HTTP error"""
        mock_result = HttpResult(400, "Bad Request", {})
        mock_post.return_value = mock_result

        adapter = GraphQLAdapter()
        with pytest.raises(HttpAdapterException) as exc_info:
            adapter.generate_access_token(refresh_token="test-token")
        assert "Failed to generate access token" in str(exc_info.value)

    @patch.object(HttpAdapter, "post")
    def test_graphql_adapter_generate_access_token_no_token_in_response(
        self, mock_post: Any
    ):
        """Test access token generation with missing token in response"""
        mock_result = HttpResult(
            200,
            "OK",
            {"data": {"generateAccessToken": {"__typename": "AccessTokenPayload"}}},
        )
        mock_post.return_value = mock_result

        adapter = GraphQLAdapter()
        with pytest.raises(HttpAdapterException) as exc_info:
            adapter.generate_access_token(refresh_token="test-token")
        assert "No access token found in response" in str(exc_info.value)

    @patch.object(HttpAdapter, "post")
    def test_graphql_adapter_generate_access_token_invalid_response(
        self, mock_post: Any
    ):
        """Test access token generation with invalid response format"""
        mock_result = HttpResult(200, "OK", {"invalid": "format"})
        mock_post.return_value = mock_result

        adapter = GraphQLAdapter()
        with pytest.raises(HttpAdapterException) as exc_info:
            adapter.generate_access_token(refresh_token="test-token")
        assert "No access token found in response" in str(exc_info.value)

    @patch.object(GraphQLAdapter, "generate_access_token")
    def test_graphql_adapter_get_access_token_class_method(self, mock_generate: Any):
        """Test class method for getting access token"""
        mock_generate.return_value = "test-token-123"

        token = GraphQLAdapter.get_access_token(
            hostname="test.com",
            ver="v2",
            protocol="http",
            refresh_token="refresh-token",
        )

        assert token == "test-token-123"
        mock_generate.assert_called_once_with(refresh_token="refresh-token")

    @patch.object(GraphQLAdapter, "generate_access_token")
    def test_graphql_adapter_get_access_token_class_method_defaults(
        self, mock_generate: Any
    ):
        """Test class method for getting access token with defaults"""
        mock_generate.return_value = "test-token-123"

        token = GraphQLAdapter.get_access_token()

        assert token == "test-token-123"
        mock_generate.assert_called_once_with(refresh_token=None)


class TestIntegration:
    """Integration tests for adapters"""

    @patch("src.adapters.requests.post")
    def test_graphql_adapter_integration_with_http_adapter(self, mock_post: Any):
        """Test that GraphQLAdapter properly uses HttpAdapter"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.url = "https://gql.poolplayers.com/graphql"
        mock_response.json.return_value = {"data": {"test": "value"}}
        mock_post.return_value = mock_response

        adapter = GraphQLAdapter()
        result = adapter.query("query { test }")

        # Verify the request was made to the correct URL
        mock_post.assert_called_once_with(
            url="https://gql.poolplayers.com/graphql",
            params=None,
            json={"query": "query { test }", "variables": {}},
        )

        assert result.status_code == 200
        assert result.data == {"data": {"test": "value"}}


if __name__ == "__main__":
    pytest.main([__file__])
