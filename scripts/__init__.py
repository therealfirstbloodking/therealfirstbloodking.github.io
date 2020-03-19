"""Scripts for finding the true first blood king."""

import os
from functools import wraps
import time

import yaml


def get_api_token(path='~/.riot_api_token'):
    """Get Riot API token."""
    path = os.path.expanduser(path)
    print(f"Reading Riot API token from {path}")
    with open(path) as infile:
        token = infile.read()
    token = token.strip('\n')
    return token


def get_config(path='config.yml'):
    """Get user configuration file."""
    with open(path, 'r') as infile:
        config = yaml.safe_load(infile)
    return config


def get_outfile(config, summoner):
    """Get outfile."""
    out_dir = os.path.expanduser(config.get('out_dir', '~'))
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
        print(f"Created '{out_dir}'")
    filename = 'matches_' + summoner.replace(' ', '_') + '.yml'
    outfile = os.path.expanduser(os.path.join(out_dir, filename))
    print(f"Writing data to '{outfile}'")
    print("")
    return outfile


def get_summoner_info(config):
    """Get summoner information."""
    summoner = config.get('summoner', ['F1rst Blood K1ng'])
    region = config.get('region', 'euw1')
    queues = config.get('queues', [450])
    if not isinstance(summoner, list):
        summoner = [summoner]
    print(f"Extracting data for summoner '{summoner[0]}' in region '{region}'")
    if len(summoner) > 1:
        print(f"Alternative summoner names for retrieving matches: "
              f"{summoner[1:]}")
    print(f"Queues: {queues}")
    return (summoner, region, queues)


def delayed_execution(delay):
    """Decorator for delayed function execution."""

    def decorator(func):
        """Decorator."""
        wraps(func)

        def wrapper(*args, **kwargs):
            """Wrapper function."""
            time.sleep(delay)
            func(*args, **kwargs)

    return decorator
