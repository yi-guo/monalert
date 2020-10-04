from datetime import datetime
from monalert import db, models
from typing import Dict, Final, List, Optional

import requests

BASE_URL: Final[
    str] = "https://nysdmvqw.us.qmatic.cloud/qwebbook/rest/schedule"

REQUESTS_HEADERS: Final[Dict[str, str]] = {
    "content-type": "application/json",
    "referer": "https://nysdmvqw.us.qmatic.cloud/qwebbook/index.jsp",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 " \
        "Safari/537.36",
}

# Manhattan - Lower Manhattan (Financial District)
BRANCH: Final[
    str] = "8bcc5ca5cad16666ba6f5dd43d15241e172bd511f7e8d6f2e1caa2380b66776a"
# Exchange Your Out of State License
SERVICE: Final[
    str] = "2cac88e280dfb5f69ecf53ace1a0c00e4d43ba8d14c55a99ee5cb52e824b7389"

MONGO_COLLECTION: Final[str] = "dmv_ny"

DATETIME_FORMAT = "%Y-%m-%d"


class DMVNewYork(models.Monalert):
    def __init__(self) -> None:
        super().__init__()
        self.__mongo_collection = db.get_mongo_database()[MONGO_COLLECTION]

    def _monitor(self) -> None:
        print(f"Retrieving the best candidate...")
        self.__current_date = self.__get_current_date()
        print(f"Checking available dates...")
        available_dates = self.__get_available_dates()
        if not available_dates:
            print(f"  => No available dates")
            return
        self.__best_available_date = available_dates[0]
        if not self.__current_date or \
            self.__best_available_date < self.__current_date:
            print(f"Setting {self.__current_date} to be the best candidate...")
            self.__set_current_date(self.__best_available_date)

    def _should_alert(self) -> bool:
        return not self.__current_date or \
            self.__best_available_date < self.__current_date

    def _get_notification(self) -> models.Notification:
        available_date = self.__datetime_to_str(self.__best_available_date)
        return models.Notification(
            title=f"New DMV Available Dates",
            message=f"Hurry! Available appointments on {available_date}!")

    def __get_available_dates(self) -> List[datetime]:
        response = requests.get(
            f"{BASE_URL}/branches/{BRANCH}/services/{SERVICE}/dates",
            headers=REQUESTS_HEADERS)
        return sorted([
            self.__str_to_datetime(available_date["date"])
            for available_date in response.json()
        ])

    def __get_current_date(self) -> Optional[datetime]:
        document = self.__mongo_collection.find_one()
        return self.__str_to_datetime(
            document.get("date")) if document else None

    def __set_current_date(self, date: datetime) -> None:
        if not self.__current_date:
            self.__mongo_collection.insert_one(
                {"date": self.__datetime_to_str(date)})
            return
        self.__mongo_collection.replace_one(
            filter={"date": self.__datetime_to_str(self.__current_date)},
            replacement={"date": self.__datetime_to_str(date)})

    @staticmethod
    def __str_to_datetime(date: str) -> datetime:
        return datetime.strptime(date, DATETIME_FORMAT)

    @staticmethod
    def __datetime_to_str(date: datetime) -> str:
        return datetime.strftime(date, DATETIME_FORMAT)
