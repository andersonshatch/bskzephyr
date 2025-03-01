import json
from enum import Enum
from http import HTTPStatus

from aiohttp import ClientResponseError
from aiohttp.client import ClientResponse, ClientSession
from pydantic import BaseModel

from .exceptions import InvalidAuthError, ZephyrException


class FanMode(str, Enum):
    cycle = "cycle"
    extract = "extract"
    supply = "supply"


class FanSpeed(int, Enum):
    night = 22
    low = 30
    medium = 55
    high = 80


class ZephyrSettings(BaseModel):
    deviceID: str | None = None
    groupID: str | None = None
    deviceStatus: str | None = None
    fanSpeed: FanSpeed
    fanMode: FanMode
    boostTime: int
    humidityBoost: int
    cycleTime: int
    cycleDirection: str
    _id: str
    deviceModel: str | None = None


class Zephyr(BaseModel):
    _id: str
    deviceID: str
    deviceModel: str
    filterTimer: int
    groupID: str
    groupTitle: str
    title: str
    humidity: float
    temperature: float
    hygieneStatus: str
    deviceStatus: str
    version: str
    settings: ZephyrSettings


class BSKZephyrClient:
    def __init__(
        self,
        session: ClientSession,
        username: str | None = None,
        password: str | None = None,
        token: str | None = None,
    ) -> None:
        self._username = username
        self._password = password
        self._token = token
        self._aiohttp_session: ClientSession = session

    async def login(self) -> str:
        try:
            resp: ClientResponse = await self._aiohttp_session.request(
                "post",
                "https://api.bskhvac.com.tr/auth/sign-in",
                json={
                    "email": self._username,
                    "password": self._password,
                },
                raise_for_status=True,
            )

            token = (await resp.json())["accessToken"]
            self._token = token
            return token
        except ClientResponseError as err:
            if err.status == HTTPStatus.FORBIDDEN:
                raise InvalidAuthError(err)
            else:
                raise ZephyrException(err)

    async def main_device_list(self) -> list[Zephyr]:
        try:
            resp: ClientResponse = await self._aiohttp_session.request(
                "get",
                "https://api.bskhvac.com.tr/device-user/zephyr/master-device-list",
                headers={"Authorization": self._token},
                raise_for_status=True,
            )
        except ClientResponseError as err:
            if err.status == HTTPStatus.UNAUTHORIZED:
                raise InvalidAuthError(err)
            else:
                raise ZephyrException(err)

        resp = await resp.json()
        models = []
        for device in resp:
            models.append(Zephyr(**device))

        return models

    async def update_group_settings(self, body) -> dict:
        print(json.dumps(body))
        resp: ClientResponse = await self._aiohttp_session.request(
            "post",
            "https://api.bskhvac.com.tr/device-user/zephyr/update-group-settings",
            headers={"Authorization": self._token},
            json=body,
            raise_for_status=True,
        )

        return await resp.json()
