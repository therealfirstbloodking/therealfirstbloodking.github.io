#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

import yaml
from riotwatcher import LolWatcher

from __init__ import get_api_token, get_config, get_outfile, get_summoner_info


def main():
    """Main function to download all desired matches of the summoner."""
    print("Welcome summoner!")
    print("")

    # Get user configuration
    api_token = get_api_token()
    config = get_config()
    (summoner, region, queues) = get_summoner_info(config)
    outfile = get_outfile(config, summoner[0])
    watcher = LolWatcher(api_token)

    # Get summoner's account ID
    summoner_id = watcher.summoner.by_name(region, summoner[0])['accountId']

    # Get desired matches
    idx = 0
    while True:
        try:
            matches = watcher.match.matchlist_by_account(
                region, summoner_id, queue=queues, begin_index=idx,
                end_index=idx + 1)['matches']
        except Exception as exc:
            print(f"Retrieving matches failed: {str(exc)}")
            time.sleep(1.0)
            continue
        if not matches:
            print("Finished successfully")
            break
        try:
            match = watcher.match.by_id(region, matches[0]['gameId'])
        except Exception as exc:
            print(f"Retrieving matches failed: {str(exc)}")
            time.sleep(1.0)
            continue

        # Save file
        with open(outfile, 'a') as file_:
            yaml.safe_dump([match], file_)
            print(f"Saved match {idx:5d} to '{outfile}'")
        idx += 1


if __name__ == '__main__':
    main()
