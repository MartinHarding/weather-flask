import os
import re
import time

"""A simple file based caching module"""

def sanitize_string(text: str) -> str:
    """Strips unsafe characters from a string

    Args:
        text (str): string to sanitize

    Returns:
        str: santized string
    """
    pattern = re.compile(r'^[a-zA-Z0-9_]*$')
    return pattern.sub('', text)

class FileCache(object):
    """A simple file based caching class"""

    def __init__(self, cache_dir: str, timeout: int):
        """
        Args:
            cache_dir (str): path to directory to store cached files
            timeout (int): default timeout in seconds for cached files
        """
        super(FileCache, self).__init__()
        self.cache_dir = cache_dir
        self.timeout = timeout

    def _cache_path(self, key: str) -> str:
        """Generate an appropriate/safe file path for the cache file

        Args:
            key (str): cache key to generate a path for

        Returns:
            str: full path to cache file
        """
        #: sanitized key name
        sanitized_key = sanitize_string(key)
        return os.path.abspath('{}/{}'.format(self.cache_dir, sanitized_key))

    def check(self, key: str, timeout: int=None) -> bool:
        """Check if a key is saved to the cache and has not expired

        Args:
            key (str): key to check
            timeout (int, optional): Defaults to self.timeout. Max cache age.

        Returns:
            bool: whether the cache key exists and is not expired
        """
        timeout = self.timeout if not timeout else timeout
        cache_path = self._cache_path(key)
        if os.path.exists(cache_path):
            cache_age = time.time() - os.path.getmtime(cache_path)
            return cache_age < timeout
        return False

    def load(self, key: str, timeout: int=None) -> str:
        """Load a key from the cache

        Args:
            key (str): cached file key
            timeout (int, optional): Defaults to self.timeout. Max cache age.

        Returns:
            str: contents of the file
        """
        timeout = self.timeout if not timeout else timeout
        if self.check(key, timeout):
            cache_path = self._cache_path(key)
            with open(cache_path, 'r') as f:
                return f.read()
        else:
            return None

    def save(self, key: str, data: str) -> bool:
        """Save data to the cache

        Args:
            key (str): key to store the data under
            data (str): data to save
        """
        cache_path = self._cache_path(key)
        with open(cache_path, 'w') as f:
            f.write(data)

