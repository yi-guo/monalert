from abc import ABC, abstractmethod
from typing import Dict, Final, List, NoReturn, Union

import os
import requests

ENV_PUSHOVER_TOKEN: Final[str] = "PUSHOVER_TOKEN"
ENV_PUSHOVER_USER: Final[str] = "PUSHOVER_USER"
ENV_PUSHOVER_DEVICE: Final[str] = "PUSHOVER_DEVICE"

PUSHOVER_URL: Final[str] = "https://api.pushover.net/1/messages.json"
PUSHOVER_REQUEST_PARAM_MESSAGE: Final[str] = "message"
PUSHOVER_RESPONSE_PARAM_STATUS: Final[str] = "status"

REQUESTS_STATUS_CODE_SUCCESS: Final[int] = 200
REQUESTS_HEADERS: Final[Dict[str, str]] = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 " \
        "Safari/537.36",
}


class Monalert(ABC):
    def __init__(self) -> None:
        envs: List[Final[str]] = [
            ENV_PUSHOVER_TOKEN,
            ENV_PUSHOVER_USER,
            ENV_PUSHOVER_DEVICE,
        ]
        for env in envs:
            if not os.getenv(env):
                raise RuntimeError(f"Missing environment variable {env}")
        self.__pushover_token: str = os.environ[ENV_PUSHOVER_TOKEN]
        self.__pushover_user: str = os.environ[ENV_PUSHOVER_USER]
        self.__pushover_device: str = os.environ[ENV_PUSHOVER_DEVICE]

    def monitor_and_alert_if_should(self) -> NoReturn:
        self._monitor()
        if self._should_alert():
            print("  => Populating notification...")
            self.__alert()
            print("  => Done! Notification sent!")
        else:
            print("  => Done! Nothing to notify!")

    @abstractmethod
    def _monitor(self) -> NoReturn:
        ...

    @abstractmethod
    def _should_alert(self) -> bool:
        ...

    @abstractmethod
    def _get_notification(self) -> Dict[str, Union[str, int]]:
        ...

    def __alert(self) -> NoReturn:
        notification: Dict[str, Union[str, int]] = self._get_notification()
        if PUSHOVER_REQUEST_PARAM_MESSAGE not in notification:
            raise ValueError(
                f"Missing notification {PUSHOVER_REQUEST_PARAM_MESSAGE}")
        response: requests.models.Response = requests.post(
            PUSHOVER_URL,
            headers=REQUESTS_HEADERS,
            data={
                "token": self.__pushover_token,
                "user": self.__pushover_user,
                "device": self.__pushover_device,
                **notification,
            },
        )
        success: bool = response.status_code == REQUESTS_STATUS_CODE_SUCCESS \
            and response.json().get(PUSHOVER_RESPONSE_PARAM_STATUS) == 1
        if not success:
            raise RuntimeError(
                f"Unable to send Notification" \
                f"<{notification[PUSHOVER_REQUEST_PARAM_MESSAGE]}>. " \
                f"Response: {response.text}")
