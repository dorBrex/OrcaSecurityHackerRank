import requests
from typing import List, Union, Dict
from dataclasses import dataclass
import asyncio
import aiohttp


@dataclass
class OutletData:
    city: str
    name: str
    estimated_cost: int
    user_rating: Dict[str, int]
    id_: int


class DataRetriever:
    def __init__(self, city: str = '', max_price: int = 0):
        self.city = city
        self.max_price = max_price
        self.all_outlets_in_the_city = []
        self.ids_collector = set()

    def get_tasks(self, session: aiohttp.ClientSession, city: str, total_page_num: int):
        tasks = []
        for page in range(total_page_num + 1):
            tasks.append(session.get(f'https://jsonmock.hackerrank.com/api/food_outlets?city={city}&page={page}'))
        return tasks

    @staticmethod
    def get_page(city: str, page_num: int):
        url = f'https://jsonmock.hackerrank.com/api/food_outlets?city={city}&page={page_num}'
        print(f'reaching page number {page_num}')
        req = requests.get(url)
        return req.json()

    async def get_all_pages(self, city: str):
        # check number of possible pages
        ans = self.get_page(city, 0)
        number_of_pages = ans['total_pages']
        print("Starting aiohttp session")
        async with aiohttp.ClientSession() as session:
            tasks = self.get_tasks(session=session, city=city, total_page_num=number_of_pages)
            responses = await asyncio.gather(*tasks)
        for resp in responses:
            resp = await resp.json()
            self._collect_data(resp['data'])

    def _collect_data(self, data: List):
        for outlet in data:
            new_outlet = OutletData(
                city=outlet['city'],
                name=outlet['name'],
                estimated_cost=outlet['estimated_cost'],
                user_rating=outlet['user_rating'],
                id_=outlet['id']
            )

            if new_outlet.id_ not in self.ids_collector:
                self.all_outlets_in_the_city.append(new_outlet)
                self.ids_collector.add(new_outlet.id_)

    def organize_data(self):
        self.all_outlets_in_the_city = sorted(self.all_outlets_in_the_city, key=lambda outlet: outlet.id_)

    def filter_outlets_by_price(self):
        good_prices_outlet = []
        for outlet in self.all_outlets_in_the_city:
            if outlet.estimated_cost <= self.max_price:
                good_prices_outlet.append(outlet.name)
        return good_prices_outlet

    async def find_best_prices_outlet_names(self) -> Union[List, None]:
        await self.get_all_pages(city=self.city)
        self.organize_data()
        good_price_outlets_name = self.filter_outlets_by_price()
        return good_price_outlets_name

    def print_all_outlets(self):
        for shop in self.all_outlets_in_the_city:
            print(shop)


class Solution:
    def __init__(self, city: str, max_price: int):
        self.city = city
        self.max_price = max_price

    async def run_solution(self):
        solution = DataRetriever(city=self.city, max_price=self.max_price)
        result_ = await solution.find_best_prices_outlet_names()
        # solution.print_all_outlets()
        return result_


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    city, max_price = 'Denver', 50
    print(f'city: {city}, max price: {max_price}')

    result = Solution(city=city, max_price=max_price)
    # try:
    ans_ = loop.run_until_complete(result.run_solution())
    # loop.run_until_complete(loop.shutdown_asyncgens())
    # finally:
    #     loop.close()


    print('The solution is: ', ans_)
    check_if_event_loop_is_closed = asyncio.get_event_loop().is_closed()
    # ToDo - check why event loop is not closing (when loop.close() - raises exception)
    loop.stop() # if I would use loop.close() - it would throw an error
    tasks = asyncio.all_tasks(loop)

    for task in tasks:
        task.cancel()
    asyncio.get_event_loop().stop()
    print(check_if_event_loop_is_closed)
