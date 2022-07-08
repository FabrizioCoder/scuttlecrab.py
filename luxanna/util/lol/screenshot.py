from io import BytesIO
from typing import Coroutine, Any
from playwright.async_api import async_playwright, Page


async def init_browser():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch()
    while True:
        yield await browser.new_page()


class Browser:
    """Singleton class to represent Playwright Browser for screenshots"""

    def __init__(self):
        self.__browser = init_browser()

    async def __new_page(self) -> Coroutine[Any, Any, Page]:
        """Creates and returns new page, caller assumes ownership and must close page"""
        try:
            return await self.__browser.__anext__()
        except Exception as e:
            print(f"Unable to get new page: \n {e}")

    async def get_cached_screenshot(self, name: str, action: str) -> BytesIO:
        img = await self.__cached_screenshot(name, action)
        return img

    async def __cached_screenshot(self, name: str, action: str) -> BytesIO:
        """Cached screenshot generator, use only for immutable (mostly) data"""
        url = f"https://www.op.gg/champion/{name}/statistics"
        page = await self.__new_page()
        try:
            await page.goto(url)
            if action == "runes":
                await page.set_viewport_size({"width": 734, "height": 607})
                await page.click(
                    "body > div.l-wrap.l-wrap--champion > div.l-container > div > div.tabWrap._recognized > div.l-champion-statistics-content.tabItems > div.tabItem.Content.championLayout-overview > div > div.l-champion-statistics-content__main > div > table"
                )
            elif action == "build":
                await page.set_viewport_size({"width": 734, "height": 667})
                await page.click(
                    "body > div.l-wrap.l-wrap--champion > div.l-container > div > div.tabWrap._recognized > div.l-champion-statistics-content.tabItems > div.tabItem.Content.championLayout-overview > div > div.l-champion-statistics-content__main > table:nth-child(2)"
                )
            elif action == "skills":
                await page.set_viewport_size({"width": 734, "height": 340})
                await page.click(
                    "body > div.l-wrap.l-wrap--champion > div.l-container > div > div.tabWrap._recognized > div.l-champion-statistics-content.tabItems > div.tabItem.Content.championLayout-overview > div > div.l-champion-statistics-content__main > table.champion-overview__table.champion-overview__table--summonerspell"
                )
            elif action == "stats":
                await page.set_viewport_size({"width": 1200, "height": 265})
                await page.click(
                    "body > div.l-wrap.l-wrap--champion > div.l-container > div > div.l-champion-statistics-header"
                )
            else:
                return None
        except Exception as e:
            print(f"Error in Cached Screenshot at: {url} :\n {e}")

        screenshot_bytes = BytesIO(await page.screenshot())
        await page.close()
        screenshot_bytes.seek(0)
        return screenshot_bytes
