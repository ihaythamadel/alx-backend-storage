#!/usr/bin/env python3
'''A module with tools for request caching and tracking.
'''
import redis
import requests
from functools import wraps
from typing import Callable


def connect_to_redis(host='localhost', port=6379):
    """Connects to a Redis server.

    Args:
        host (str, optional): The hostname or IP address of the Redis server.
            Defaults to 'localhost'.
        port (int, optional): The port number of the Redis server. Defaults to 6379.

    Returns:
        redis.Redis: A Redis client object.
    """
    return redis.Redis(host=host, port=port)


redis_store = connect_to_redis()


def data_cacher(method: Callable) -> Callable:
    '''Caches the output of fetched data.
    '''
    @wraps(method)
    def invoker(url: str) -> str:
        '''The wrapper function for caching the output.
        '''
        # Increment request count for tracking
        redis_store.incr(f'count:{url}')

        # Check cache for existing result
        result = redis_store.get(f'result:{url}')
        if result:
            return result.decode('utf-8')

        # Fetch data if not cached
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise error for non-2xx status codes
            result = response.text
        except requests.RequestException as e:
            # Handle request exceptions (e.g., network errors)
            print(f"Error fetching data for {url}: {e}")
            return None

        # Update cache and reset request count
        redis_store.set(f'count:{url}', 0)
        redis_store.setex(f'result:{url}', 10, result)
        return result

    return invoker


@data_cacher
def get_page(url: str) -> str:
    '''Returns the content of a URL after caching the request's response,
    and tracking the request.
    '''
    return requests.get(url).text


if __name__ == "__main__":
    # Example usage
    url = "https://www.example.com"
    content = get_page(url)
    if content:
        print(f"Fetched content for {url}: {content[:100]}...")
    else:
        print(f"Error fetching content for {url}")
