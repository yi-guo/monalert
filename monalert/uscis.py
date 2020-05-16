from bs4 import BeautifulSoup, element
from dataclasses import dataclass
from datetime import datetime
from monalert import db, models
from typing import Dict, Final, List, Optional

import pymongo
import requests

USCIS_URL: Final[str] = "https://egov.uscis.gov/casestatus/mycasestatus.do"

REQUESTS_HEADERS: Final[Dict[str, str]] = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "egov.uscis.gov",
    "Origin": "https://egov.uscis.gov",
    "Referer": "https://egov.uscis.gov/casestatus/mycasestatus.do",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 " \
        "Safari/537.36",
}

HTML_PARSER: Final[str] = "html.parser"
HTML_CLASS_CURR_STATUS: Final[str] = "rows text-center"

MONGO_COLLECTION: Final[str] = "uscis"

MASK_CHARACTER: Final[str] = "*"
MASK_LENGTH_REMAINING: Final[int] = 4


@dataclass(frozen=True)
class Status():
    utc_time: datetime
    receipt_num: str
    status: str
    description: str


class USCIS(models.Monalert):
    def __init__(self, receipt_num: str) -> None:
        super().__init__()
        self.__receipt_num: str = receipt_num
        self.__mongo_collection: pymongo.collection.Collection = \
            db.get_mongo_database()[MONGO_COLLECTION]

    def _monitor(self) -> None:
        print(f"Checking USCIS<{self.__receipt_num}>...")
        self.__prev_status: Optional[Status] = self.__get_prev_status()
        self.__curr_status: Status = self.__get_curr_status()
        print(f"  => Current status: {self.__curr_status.status}")
        self.__save_curr_status(self.__curr_status)
        print(f"  => Status saved")

    def _should_alert(self) -> bool:
        return self.__prev_status is None \
            or self.__prev_status.status != self.__curr_status.status

    def _get_notification(self) -> models.Notification:
        receipt_num_masked: str = self.__get_receipt_num_masked()
        return models.Notification(
            title=f"USCIS {receipt_num_masked}: {self.__curr_status.status}",
            message=self.__curr_status.description.replace(
                self.__receipt_num,
                receipt_num_masked,
            ),
        )

    def __get_curr_status(self) -> Status:
        response: requests.models.Response = requests.post(
            USCIS_URL,
            headers=REQUESTS_HEADERS,
            data={
                "appReceiptNum": self.__receipt_num,
            },
        )
        bs: BeautifulSoup = BeautifulSoup(response.text, HTML_PARSER)
        tags_curr_status: List[element.Tag] = bs.find_all(
            class_=HTML_CLASS_CURR_STATUS)
        if len(tags_curr_status) != 1:
            raise RuntimeError(
                f"Unable to retrieve current status for application " \
                f"{self.__receipt_num}")
        tag_curr_status: Optional[element.Tag] = tags_curr_status[0].h1
        tag_curr_status_description: Optional[element.Tag] = \
            tags_curr_status[0].p
        if tag_curr_status is None or tag_curr_status_description is None:
            raise RuntimeError(
                f"Unable to retrieve current status for application " \
                f"{self.__receipt_num}")
        return Status(
            utc_time=datetime.utcnow(),
            receipt_num=self.__receipt_num,
            status=tag_curr_status.text.strip(),
            description=tag_curr_status_description.text.strip(),
        )

    def __get_prev_status(self) -> Optional[Status]:
        cursor: pymongo.cursor.Cursor = self.__mongo_collection.find({
            "receipt_num":
            self.__receipt_num
        }).sort(
            "utc_time",
            direction=pymongo.DESCENDING,
        ).limit(1)
        return None if cursor.count() == 0 else Status(
            utc_time=cursor[0]["utc_time"],
            receipt_num=cursor[0]["receipt_num"],
            status=cursor[0]["status"],
            description=cursor[0]["description"],
        )

    def __save_curr_status(self, curr_status: Status) -> None:
        self.__mongo_collection.insert_one(curr_status)

    def __get_receipt_num_masked(self) -> str:
        return self.__receipt_num[-MASK_LENGTH_REMAINING:].rjust(
            len(self.__receipt_num),
            MASK_CHARACTER,
        )
