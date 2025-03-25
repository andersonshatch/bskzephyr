from enum import Enum
from http import HTTPStatus

from aiohttp import ClientResponseError, ContentTypeError
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


class Zephyr(BaseModel):
    _id: str
    boostTime: int
    buzzerEnable: int
    cycleDirection: str
    cycleTime: int
    deviceID: str
    deviceModel: str
    deviceStatus: str
    fanSpeed: FanSpeed
    fanMode: FanMode
    filterTimer: int
    groupID: str
    humidity: float
    humidityBoost: int
    humidityBoostState: bool
    hygieneStatus: int
    temperature: float
    type: str
    updatedAt: str
    version: str


class DeviceUser(BaseModel):
    _id: str
    DeviceUserType: str
    createdAt: str
    device: Zephyr
    deviceModel: str
    groupTitle: str
    title: str
    updatedAt: str
    user: str


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
        async with self._aiohttp_session.request(
            "post",
            "https://connect.bskhvac.com.tr/auth/sign-in",
            json={
                "email": self._username,
                "password": self._password,
            },
            raise_for_status=False,
        ) as resp:
            if resp.status == HTTPStatus.OK:
                token = (await resp.json())["accessToken"]
                self._token = token
                return token
            elif resp.status in (
                HTTPStatus.FORBIDDEN,
                HTTPStatus.INTERNAL_SERVER_ERROR,
            ):
                try:
                    body = await resp.json()
                except ContentTypeError:
                    raise ZephyrException(resp.status)
                message = body.get("message")
                raise InvalidAuthError(message)
            else:
                raise ZephyrException(resp.status)

    async def list_devices(self) -> list[DeviceUser]:
        try:
            resp: ClientResponse = await self._aiohttp_session.request(
                "get",
                "https://connect.bskhvac.com.tr/device-user",
                headers={"Authorization": self._token},
                raise_for_status=True,
            )

            resp = await resp.json()
            models = []
            for device in resp:
                models.append(DeviceUser(**device))

            return models
        except ClientResponseError as err:
            if err.status == HTTPStatus.UNAUTHORIZED:
                raise InvalidAuthError(err)
            else:
                raise ZephyrException(err)

    async def control_device(
        self,
        groupID: str,
        deviceStatus: str | None = None,
        fanMode: FanMode | None = None,
        fanSpeed: FanSpeed | None = None,
        humidityBoost: int | None = None,
    ) -> Zephyr | None:
        body = {}
        if deviceStatus:
            body["deviceStatus"] = deviceStatus
        if fanMode:
            body["fanMode"] = fanMode
        if fanSpeed:
            body["fanSpeed"] = fanSpeed
        if humidityBoost is not None:  # allow 0
            body["humidityBoost"] = humidityBoost

        if not body:
            return None

        try:
            resp: ClientResponse = await self._aiohttp_session.request(
                "put",
                f"https://connect.bskhvac.com.tr/device?groupID={groupID}",
                headers={"Authorization": self._token},
                json=body,
                raise_for_status=True,
            )

            return Zephyr(**(await resp.json()))
        except ClientResponseError as err:
            raise ZephyrException from err
