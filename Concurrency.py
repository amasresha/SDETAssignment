import API_Requests as req, Helpers as hp
import asyncio
import aiohttp
file_name = 'valid_pswd_string_only.JSON'
url =""


async def fetch(session, url):
    async with session.req.get_post_response(file_name) as response:
        json_response= await response.json()
        print(json_response)

async def main ():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session) for _ in range(5)]
        await asyncio.gather(*tasks)


print ("hello")


