import logging
from typing import Dict, List

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
        if "copyright" in data:
            del data["copyright"]


class HttpAdapter:
    """
    Generic HTTP adapter for making API calls to external services

    Attributes
    ----------
    hostname : str
        rest endpoint for data
    ver : str
        api version
    logger : logging.Logger
        instance of logger class
    """

    def __init__(
        self,
        hostname: str = "api.example.com",
        ver: str = "v1",
        logger: logging.Logger = None,
    ):
        self.url = f"https://{hostname}/api/{ver}/"
        self._logger = logger or logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

    def _transform_keys_in_data(self, data) -> dict:
        """
        Recursively transform all the keys in a dictionary to lowercase

        Parameters
        ----------
        data : dict
            HttpResult data dictionary

        Returns
        -------
        dict
        """

        if isinstance(data, Dict):
            lowered_dict = {}

            for key, value in data.items():
                lowered_dict[key.lower()] = self._transform_keys_in_data(value)

            return lowered_dict

        elif isinstance(data, List):
            lowered_list = []

            for item in data:
                lowered_list.append(self._transform_keys_in_data(item))

            return lowered_list

        else:
            return data

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
        print(full_url)
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

            data = self._transform_keys_in_data(data)
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
