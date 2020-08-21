import logging
import aiohttp
import asyncio

logger = logging.getLogger(__name__)

session = aiohttp.ClientSession()


async def get_ip(pro):
    if pro == "全国" or pro is None:
        pro = ""
    ip_address = f""
    try:
        async with session.get(ip_address) as resp:
            result = await resp.json(content_type="text/html")
        # result = requests.get(ip_address).json()
    except:
        await asyncio.sleep(1)
        return await get_ip(pro)
    code = result.get("code")
    if code == 0:
        return result.get("data")[0]
    elif code == 5:
        current_ip = result.get("msg").split("登录IP")[0]
        add_user_url = f""
        async with session.get(add_user_url) as resp:
            result = await resp.json(content_type="text/html")
        # result = requests.get(add_user_url).json()
            if result.get("code") != 0:
                logger.debug(result.get("msg"))
                return None
            else:
                return await get_ip(pro)
    elif code == 10000:
        await asyncio.sleep(1)
        return await get_ip(pro)
    else:
        logger.debug(result.get("msg"))
        return None
