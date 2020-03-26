"""Scripts for finding the true first blood king."""

import os
import time
from functools import wraps
from pprint import pprint

import yaml


DATA_FILE = 'all_data.yml'
MATCHES_PREFIX = 'matches_'


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


def get_data_dir(config):
    """Get directory where data is/will be stored."""
    data_dir = os.path.expanduser(config.get('data_dir', '~'))
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)
        print(f"Created '{data_dir}'")
    return data_dir


def get_plot_dir(config, absolute=True):
    """Get directory where plots is/will be stored."""
    plot_dir = config.get('plot_dir', 'img')
    if absolute:
        plot_dir = os.path.abspath(os.path.join('..', plot_dir))
        if not os.path.isdir(plot_dir):
            os.makedirs(plot_dir)
            print(f"Created '{plot_dir}'")
    return plot_dir


def get_matches_filename(config, summoner):
    """Get name of file that contains all matches of given summoner."""
    data_dir = get_data_dir(config)
    filename = MATCHES_PREFIX + summoner.replace(' ', '_') + '.yml'
    matches_file = os.path.expanduser(os.path.join(data_dir, filename))
    print(f"Writing matches of summoner {summoner} to '{matches_file}'")
    return matches_file


def get_queues(config):
    """Get queues from configuration :obj:`dict`."""
    queues = config.get('queues', [450])
    print(f"Found queues: {queues}")
    return queues


def get_region(config):
    """Get region from configuration :obj:`dict`."""
    region = config.get('region', 'euw1')
    print(f"Found region: {region}")
    return region


def get_summoners(config):
    """Get summoners from configuration :obj:`dict`."""
    summoners = config.get('summoners', [])
    for (idx, summoner) in enumerate(summoners):
        if not isinstance(summoner, list):
            summoners[idx] = [summoner]
    print("Found summoners:")
    pprint(summoners)
    return summoners


def delayed_execution(delay):
    """Decorator for delayed function execution."""

    def decorator(func):
        """Decorator."""
        wraps(func)

        def wrapper(*args, **kwargs):
            """Wrapper function."""
            time.sleep(delay)
            return func(*args, **kwargs)

    return decorator
