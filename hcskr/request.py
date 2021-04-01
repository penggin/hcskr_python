from typing import Dict
import aiohttp


async def send_hcsreq(headers: Dict, endpoint: str, school: str, json: Dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            headers=headers, url=f"https://{school}hcs.eduro.go.kr{endpoint}", json=json
        ) as resp:

            return await resp.json()


async def search_school(code: str, level: str, org: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url=f"https://hcs.eduro.go.kr/v2/searchSchool?lctnScCode={code}&schulCrseScCode={level}&orgName={org}&loginType=school"
        ) as resp:
            return await resp.json()
