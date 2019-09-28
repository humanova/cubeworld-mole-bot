from aiohttp import ClientSession

async def post(content, url='https://hastebin.com'):
    async with ClientSession() as session:
        async with session.post(f'{url}/documents', data=content.encode('utf-8')) as post:
            return url + '/' + (await post.json())['key']