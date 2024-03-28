#!/usr/bin/env python3
"""
    will implement a get_page function (prototype:
    def get_page(url: str) -> str:).
"""
import redis
import requests
from functools import wraps
from typing import Callable


redis_store = redis.Redis()
"""
A module-level Redis instance.
"""


def data_cacher(method: Callable) -> Callable:
    """
    to get the output of fetched data.
    """
    @wraps(method)
    def invoker(url) -> str:
        """
        for caching the output ,A wrapper function used.
        """
        redis_store.incr(f'count:{url}')
        result = redis_store.get(f'result:{url}')
        if result:
            return result.decode('utf-8')
        result = method(url)
        redis_store.set(f'count:{url}', 0)
        redis_store.setex(f'result:{url}', 10, result)
        return result
    return invoker


@data_cacher
def get_page(url: str) -> str:
    """
    caching the request's response, and tracking the request.
    then will returns the content of a URL after 
    """
    return requests.get(url).text