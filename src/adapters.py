import logging
import os
from typing import Dict

import requests

from .exceptions import HttpAdapterException


class HttpResult:
    """
    A class that holds data, status_code, and message returned from HTTP API calls

    Attributes
    ----------
    status_code : int
        HTTP Return Code
    message : str
        Message returned from REST Endpoint
    data : dict
        JSON Data received from request
    """

    def __init__(self, status_code: int, message: str, data: Dict = {}):
        self.status_code = int(status_code)
        self.message = str(message)

        self.data = data


class HttpAdapter:
    """
    Generic HTTP adapter for making API calls to external services

    Attributes
    ----------
    hostname : str
        rest endpoint for data
    ver : str
        api version
    protocol : str
        protocol for the API
    logger : logging.Logger
        instance of logger class
    """

    def __init__(
        self,
        ver: str = None,
        base_url: str = None,
        hostname: str = "api.example.com",
        protocol: str = "https",
        logger: logging.Logger = None,
    ):
        if base_url and ver:
            self.url = f"{protocol}://{hostname}/{base_url}/{ver}/"
        elif base_url:
            self.url = f"{protocol}://{hostname}/{base_url}/"
        elif ver:
            self.url = f"{protocol}://{hostname}/{ver}/"
        else:
            self.url = f"{protocol}://{hostname}/"

        self._logger = logger or logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

    def get(
        self, endpoint: str, ep_params: Dict = None, data: Dict = None
    ) -> HttpResult:
        """
        Return a HttpResult from endpoint

        Parameters
        ----------
        endpoint : str
            rest api endpoint
        ep_params : dict
            params
        data : dict
            data to send with requests (we aren't using this)

        Returns
        -------
        HttpResult
        """

        full_url = self.url + endpoint
        logline_pre = f"url={full_url}"
        logline_post = " ,".join(
            (logline_pre, "success={}, status_code={}, message={}, url={}")
        )

        try:
            self._logger.debug(logline_post)
            response = requests.get(url=full_url, params=ep_params)

        except requests.exceptions.RequestException as e:
            self._logger.error(msg=(str(e)))
            raise HttpAdapterException("Request failed") from e

        try:
            data = response.json()

        except (ValueError, requests.JSONDecodeError) as e:
            self._logger.error(msg=(str(e)))
            raise HttpAdapterException("Bad JSON in response") from e

        if 200 <= response.status_code <= 299:
            self._logger.debug(
                msg=logline_post.format(
                    "success", response.status_code, response.reason, response.url
                )
            )

            return HttpResult(response.status_code, message=response.reason, data=data)

        elif 400 <= response.status_code <= 499:
            self._logger.error(
                msg=logline_post.format(
                    "Invalid Request",
                    response.status_code,
                    response.reason,
                    response.url,
                )
            )

            # return HttpResult with 404 and empty data
            return HttpResult(response.status_code, message=response.reason, data={})

        elif 500 <= response.status_code <= 599:
            self._logger.error(
                msg=logline_post.format(
                    "Internal error occurred",
                    response.status_code,
                    response.reason,
                    response.url,
                )
            )

            raise HttpAdapterException(f"{response.status_code}: {response.reason}")

        else:
            raise HttpAdapterException(f"{response.status_code}: {response.reason}")

    def post(
        self, endpoint: str, ep_params: Dict = None, data: Dict = None
    ) -> HttpResult:
        """
        Return a HttpResult from endpoint
        """
        full_url = self.url + endpoint
        logline_pre = f"url={full_url}"
        logline_post = " ,".join(
            (logline_pre, "success={}, status_code={}, message={}, url={}")
        )
        try:
            self._logger.debug(logline_post)
            response = requests.post(url=full_url, params=ep_params, json=data)

        except requests.exceptions.RequestException as e:
            self._logger.error(msg=(str(e)))
            raise HttpAdapterException("Request failed") from e

        try:
            data = response.json()

        except (ValueError, requests.JSONDecodeError) as e:
            self._logger.error(msg=(str(e)))
            raise HttpAdapterException("Bad JSON in response") from e

        if 200 <= response.status_code <= 299:
            self._logger.debug(
                msg=logline_post.format(
                    "success", response.status_code, response.reason, response.url
                )
            )

            return HttpResult(response.status_code, message=response.reason, data=data)

        elif 400 <= response.status_code <= 499:
            self._logger.error(
                msg=logline_post.format(
                    "Invalid Request",
                    response.status_code,
                    response.reason,
                    response.url,
                )
            )

            # return HttpResult with 404 and empty data
            return HttpResult(response.status_code, message=response.reason, data={})

        elif 500 <= response.status_code <= 599:
            self._logger.error(
                msg=logline_post.format(
                    "Internal error occurred",
                    response.status_code,
                    response.reason,
                    response.url,
                )
            )

            raise HttpAdapterException(f"{response.status_code}: {response.reason}")

        else:
            raise HttpAdapterException(f"{response.status_code}: {response.reason}")


class GraphQLAdapter:
    """
    Generic GraphQL adapter for making API calls to external services

    Uses HttpAdapter internally for HTTP communication and adds GraphQL-specific
    functionality like query and mutation handling.

    Attributes
    ----------
    http_adapter : HttpAdapter
        Internal HTTP adapter for making requests
    endpoint : str
        GraphQL endpoint URL
    logger : logging.Logger
        instance of logger class
    """

    def __init__(
        self,
        ver: str = None,
        base_url: str = None,
        hostname: str = "gql.poolplayers.com",
        protocol: str = "https",
        logger: logging.Logger = None,
    ):
        self._logger = logger or logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

        if base_url and ver:
            self.http_adapter = HttpAdapter(
                hostname=hostname,
                ver=ver,
                base_url=base_url,
                protocol=protocol,
                logger=logger,
            )
        elif base_url:
            self.http_adapter = HttpAdapter(
                hostname=hostname, base_url=base_url, protocol=protocol, logger=logger
            )
        elif ver:
            self.http_adapter = HttpAdapter(
                hostname=hostname, ver=ver, protocol=protocol, logger=logger
            )
        else:
            self.http_adapter = HttpAdapter(
                hostname=hostname, protocol=protocol, logger=logger
            )

    def query(
        self, query: str, variables: Dict = None, operation_name: str = None
    ) -> HttpResult:
        """
        Execute a GraphQL query

        Parameters
        ----------
        query : str
            GraphQL query string
        variables : dict, optional
            Variables for the GraphQL query
        operation_name : str, optional
            Name of the operation (useful for multiple operations in one query)

        Returns
        -------
        HttpResult
            Contains the GraphQL response data and status
        """
        payload = {
            "query": query,
            "variables": variables or {},
        }

        if operation_name:
            payload["operationName"] = operation_name

        return self.http_adapter.post(endpoint="graphql", data=payload)

    def mutation(
        self, mutation: str, variables: Dict = None, operation_name: str = None
    ) -> HttpResult:
        """
        Execute a GraphQL mutation

        Parameters
        ----------
        mutation : str
            GraphQL mutation string
        variables : dict, optional
            Variables for the GraphQL mutation
        operation_name : str, optional
            Name of the operation

        Returns
        -------
        HttpResult
            Contains the GraphQL response data and status
        """
        payload = {
            "query": mutation,
            "variables": variables or {},
        }

        if operation_name:
            payload["operationName"] = operation_name

        return self.http_adapter.post(endpoint="graphql", data=payload)

    def generate_access_token(self, refresh_token: str = None) -> str:
        """
        Generate a new access token using a refresh token

        Parameters
        ----------
        refresh_token : str, optional
            The refresh token to use for generating a new access token.
            If not provided, will use APA_REFRESH_TOKEN environment variable.

        Returns
        -------
        str
            The generated access token

        Raises
        ------
        HttpAdapterException
            If token generation fails or refresh token is not available
        """
        # Use provided refresh token or get from environment
        if refresh_token is None:
            refresh_token = os.environ.get("APA_REFRESH_TOKEN")
            if not refresh_token:
                raise HttpAdapterException(
                    "No refresh token provided and "
                    "APA_REFRESH_TOKEN environment variable not set"
                )

        # GraphQL mutation for generating access token
        mutation = """
        mutation GenerateAccessTokenMutation($refreshToken: String!) {
          generateAccessToken(refreshToken: $refreshToken) {
            accessToken
            __typename
          }
        }
        """

        variables = {"refreshToken": refresh_token}

        # Make the GraphQL request
        result = self.mutation(mutation, variables=variables)

        # Check if request was successful
        if result.status_code != 200:
            raise HttpAdapterException(
                f"Failed to generate access token: {result.message}"
            )

        # Extract the access token from the response
        try:
            data = result.data.get("data", {})
            access_token = data.get("generateAccessToken", {}).get("accessToken")

            if not access_token:
                raise HttpAdapterException("No access token found in response")

            return access_token

        except (KeyError, TypeError) as e:
            raise HttpAdapterException(f"Invalid response format: {str(e)}")

    @classmethod
    def get_access_token(
        cls,
        hostname: str = "gql.poolplayers.com",
        ver: str = "v1",
        protocol: str = "https",
        refresh_token: str = None,
    ) -> str:
        """
        Class method to quickly get a new access token

        Parameters
        ----------
        hostname : str
            The API hostname
        ver : str
            The API version
        protocol : str
            The protocol to use (http or https)
        refresh_token : str, optional
            The refresh token to use. If not provided, will use
            APA_REFRESH_TOKEN environment variable.

        Returns
        -------
        str
            The generated access token
        """
        adapter = cls(hostname=hostname, ver=ver, protocol=protocol)
        return adapter.generate_access_token(refresh_token=refresh_token)
