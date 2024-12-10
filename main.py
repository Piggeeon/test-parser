from random import randint

import aiohttp
import asyncio
import fake_useragent

fio = "Гребнева Евгения"
birthdate = "1984-09-22"


async def load_page_data(url, headers, params):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            return data


def add_candidates(candidates: list, data: dict, fio):
    for person in data["pageData"]:
        if fio.lower() in person["fio"].lower():
            candidates.append(person["guid"])


async def get_legal_cases_list(headers, guid):
    url = "https://fedresurs.ru/backend/persons/" + guid + "/bankruptcy"

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            return data["legalCases"]


async def find_candidate(birthdate, candidates):

    for guid in candidates:
        await asyncio.sleep(randint(5, 10))
        user_agent = fake_useragent.UserAgent().random
        url = "https://fedresurs.ru/backend/persons/" + guid

        headers = {
            "sec-ch-ua-platform": '"Windows"',
            "Cache-Control": "no-cache",
            "Referer": "https://fedresurs.ru/persons/" + guid,
            "Pragma": "no-cache",
            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "User-Agent": user_agent,
            "Accept": "application/json, text/plain, */*"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()

            if birthdate in data["birthdateBankruptcy"]:
                return await get_legal_cases_list(headers, guid)


async def main():
    user_agent = fake_useragent.UserAgent().random

    url = "https://bankrot.fedresurs.ru/backend/prsnbankrupts"

    limit = 15
    offset = 0
    querystring = {"searchString": fio, "limit": limit, "offset": offset}

    headers = {
        "cookie": "qrator_msid=1733755982.988.GvJ3OchFhMsL92Bi-6s6oe93jc3adfte7e8jnvhkruj8u8p3d",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Cookie": "_ym_uid=1733656594226305599; _ym_d=1733656594; qrator_msid=1733755982.988.GvJ3OchFhMsL92Bi-i5ru3u4at0bfj0oohs5iumnt25dl1d4h; _ym_isad=2; _ym_visorc=b",
        "Referer": "https://bankrot.fedresurs.ru/bankrupts?searchString=" + fio,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": user_agent,
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"'
    }

    candidates = []

    first_page = await(load_page_data(url, headers, querystring))

    add_candidates(candidates, first_page, fio)

    total = first_page["total"]
    pages_count = (total // limit) + 1

    for i in range(pages_count):
        await asyncio.sleep(randint(5, 10))
        querystring["offset"] += 15
        data = await load_page_data(url, headers, querystring)

        add_candidates(candidates, data, fio)

    legal_cases = await find_candidate(birthdate, candidates)

    person = fio + " " + birthdate
    res = {person: []}
    for case in legal_cases:
        res[person].append(case["number"])

    print(res)

if __name__ == "__main__":
    asyncio.run(main())
