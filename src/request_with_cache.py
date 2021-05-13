import requests
import json

PERMANENT_CACHE_FNAME = "permanent_cache.txt"
TEMP_CACHE_FNAME = "temp_cache.txt"


def _write_to_file(cache, fname):
    with open(fname, 'w') as outfile:
        outfile.write(json.dumps(cache, indent=2))


def _read_from_file(fname):
    try:
        with open(fname, 'r') as infile:
            res = infile.read()
            return json.loads(res)
    except OSError:
        return {}


def add_to_cache(cache_file, cache_key, cache_value):
    temp_cache = _read_from_file(cache_file)
    temp_cache[cache_key] = cache_value
    _write_to_file(temp_cache, cache_file)


def clear_cache(cache_file=TEMP_CACHE_FNAME):
    _write_to_file({}, cache_file)


def requestURL(baseurl, params=dict):
    # This function accepts a URL path and a params diction as inputs.
    # It calls requests.get() with those inputs,
    # and returns the full URL of the data you want to get.
    req = requests.Request(method='GET', url=baseurl, params=params)
    prepped = req.prepare()
    return prepped.url


def get(baseurl, params=dict, permanent_cache_file=PERMANENT_CACHE_FNAME,
        temp_cache_file=TEMP_CACHE_FNAME):
    full_url = requestURL(baseurl, params)
    # Load the permanent and page-specific caches from files
    permanent_cache = _read_from_file(permanent_cache_file)
    temp_cache = _read_from_file(temp_cache_file)
    if full_url in temp_cache:
        # print("found in temp_cache")
        # make a Response object containing text from the change, and the full_url that would have been fetched
        return json.loads(temp_cache[full_url])
    elif full_url in permanent_cache:
        # print("found in permanent_cache")
        # make a Response object containing text from the change, and the full_url that would have been fetched
        return json.loads(permanent_cache[full_url])
    else:
        # print("new; adding to cache")
        # actually request it
        resp = requests.get(baseurl, params)
        # save it
        add_to_cache(temp_cache_file, full_url, resp.text)
        return resp.json()
