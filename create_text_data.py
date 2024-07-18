import random
import time
from typing import Callable, Iterator
from crawler import Crawler 
import os
import json
import re
import unicodedata
from pathlib import Path

def slugify(value, allow_unicode=False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def retry_with_backoff(fn: Callable[[], Iterator[dict]], retries=5, backoff_in_seconds=1) -> Iterator[dict]:
    x = 0
    while True:
        try:
            return fn()
        except:
            if x == retries:
                raise
            sleep = (backoff_in_seconds * 2 ** x + random.uniform(0, 1))
            time.sleep(sleep)
            x += 1

reddit = Crawler()

current_dir = os.path.dirname(os.path.abspath(__file__))
dir_path = os.path.join(current_dir, "text_data")
Path(dir_path).mkdir(parents=True, exist_ok=True)

if not os.path.exists(dir_path):
    raise FileExistsError(F"the directory {dir_path} was not created")

for sub in retry_with_backoff(reddit.load, retries=5):
    filename = "_".join((str(sub["metadata"]["score"]), sub["metadata"]["subreddit"], sub["metadata"]["title"]))
    filename = slugify(filename)
    with open(os.path.join(dir_path, filename), 'w') as file:
        file.write(json.dumps(sub))
        file.close()