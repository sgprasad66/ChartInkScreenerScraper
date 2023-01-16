import aiohttp
import asyncio
import time
from bs4 import BeautifulSoup


async def parse_page(page, session):
    async with session.get(page) as response:
        raw_text = await response.text()
        soup = BeautifulSoup(raw_text, 'html.parser')
        title_text = soup.find('h1').text
        return {'title': title_text}


async def main():
    sites = ['https://httpbin.org/html'] * 100

    start_time = time.time()

    tasks = []
    async with aiohttp.ClientSession() as session:
        for site in sites:
            tasks.append(parse_page(site, session))
        titles = await asyncio.gather(*tasks)

    print(len(titles))

    duration = time.time() - start_time
    print(f"The program run for {duration} seconds")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())