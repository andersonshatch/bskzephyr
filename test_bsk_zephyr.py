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
            "User-Agent": "BSKConnect/2 CFNetwork/3826.400.120 Darwin/24.3.0",
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
        devices = await client.list_devices()
        print(devices[0])
    except ZephyrException as e:
        print(e)
        exit(1)

    speed = (
        FanSpeed.high
        if devices[0].device.fanSpeed == FanSpeed.night
        else FanSpeed.night
    )

    print(
        await client.control_device(
            devices[0].device.groupID, "On", FanMode.cycle, speed
        )
    )

    await session.close()


if __name__ == "__main__":
    asyncio.run(main())
