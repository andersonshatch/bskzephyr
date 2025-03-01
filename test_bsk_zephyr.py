import asyncio

from aiohttp.client import ClientSession

from bskzephyr import BSKZephyrClient, FanMode, FanSpeed
from bskzephyr.exceptions import ZephyrException

USERNAME = "zzz"
PASSWORD = "zzz"
TOKEN = "zzz"


async def main():
    session = ClientSession(
        headers={
            "Accept": "application/json, text/plain, */*",
            "Accept-Lanugage": "en-GB,en;q=0.9",
            "Content-Type": "application/json",
            "User-Agent": "BSKZephyrApp/1 CFNetwork/3826.400.120 Darwin/24.3.0",
        },
    )
    client = BSKZephyrClient(
        session,
        USERNAME,
        PASSWORD,
        TOKEN,
    )
    print(await client.login())
    devices = []
    try:
        devices = await client.main_device_list()
        print(devices[0])
    except ZephyrException as e:
        print(e)
        exit(1)

    devices[0].settings.deviceID = devices[0].deviceID
    devices[0].settings.groupID = devices[0].groupID
    devices[0].settings.fanSpeed = FanSpeed.night
    devices[0].settings.fanMode = FanMode.cycle

    print(await client.update_group_settings(dict(devices[0].settings)))

    await session.close()


if __name__ == "__main__":
    asyncio.run(main())
