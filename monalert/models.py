from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Dict, Final, List, Optional

import os
import requests

ENV_PUSHOVER_TOKEN: Final[str] = "PUSHOVER_TOKEN"
ENV_PUSHOVER_USER: Final[str] = "PUSHOVER_USER"
ENV_PUSHOVER_DEVICE: Final[str] = "PUSHOVER_DEVICE"

PUSHOVER_URL: Final[str] = "https://api.pushover.net/1/messages.json"
PUSHOVER_RESPONSE_STATUS: Final[str] = "status"
PUSHOVER_RESPONSE_STATUS_DEFAULT: Final[int] = 0
PUSHOVER_RESPONSE_STATUS_SUCCESS: Final[int] = 1

HTTP_HEADERS: Final[Dict[str, str]] = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 " \
        "Safari/537.36",
}


@dataclass(frozen=True)
class Notification:
    message: str
    title: Optional[str] = None


class Monalert(ABC):
    def __init__(self) -> None:
        envs: List[str] = [
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

    def monitor_and_alert_if_should(self) -> None:
        self._monitor()
        if self._should_alert():
            print("  => Populating notification...")
            self.__alert()
            print("  => Done! Notification sent!")
        else:
            print("  => Done! Nothing to notify!")

    @abstractmethod
    def _monitor(self) -> None:
        ...

    @abstractmethod
    def _should_alert(self) -> bool:
        ...

    @abstractmethod
    def _get_notification(self) -> Notification:
        ...

    def __alert(self) -> None:
        response: requests.models.Response = requests.post(
            PUSHOVER_URL,
            headers=HTTP_HEADERS,
            data={
                "token": self.__pushover_token,
                "user": self.__pushover_user,
                "device": self.__pushover_device,
                **asdict(self._get_notification()),
            },
        )
        pushover_status: int = int(response.json().get(
            PUSHOVER_RESPONSE_STATUS,
            PUSHOVER_RESPONSE_STATUS_DEFAULT,
        ))
        if pushover_status != PUSHOVER_RESPONSE_STATUS_SUCCESS:
            raise RuntimeError(f"Unable to send Notification: {response.text}")
