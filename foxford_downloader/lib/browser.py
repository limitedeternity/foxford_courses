import asyncio

from async_lru import alru_cache
from pyppeteer import connect, launch


@alru_cache(maxsize=1, typed=False)
async def get_browser_connection_url() -> str:
    browser = await launch(
        ignoreHTTPSErrors=True,
        headless=True,
        slowMo=0,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            '--proxy-server="direct://"',
            "--proxy-bypass-list=*"
        ]
    )

    connectionUrl = browser.wsEndpoint
    await browser.disconnect()
    return connectionUrl


async def terminate_browser_instance() -> None:
    browser_endpoint = await get_browser_connection_url()
    browser = await connect(browserWSEndpoint=browser_endpoint)
    get_browser_connection_url.cache_clear()
    await browser.close()
