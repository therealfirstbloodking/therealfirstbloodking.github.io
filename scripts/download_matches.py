#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time

import yaml
from riotwatcher import LolWatcher

from __init__ import (get_api_token, get_config, get_matches_filename,
                      get_queues, get_region, get_summoners)


# Only retrieve data for given summoner for every match if desired
CROP_MATCHES = True


def get_summoner_stats(match, summoner):
    """Get only summoner's stats for a certain match."""
    all_participants = []
    for participant_id in match['participantIdentities']:
        all_participants.append(participant_id['player']['summonerName'])
        if participant_id['player']['summonerName'] in summoner:
            summoner_id = participant_id['participantId']
            break
    else:
        raise ValueError(
            f"Summoner '{summoner}' not found in match, only summoners "
            f"{all_participants} available")
    for participant in match['participants']:
        if participant['participantId'] == summoner_id:
            return participant
    raise ValueError(
        f"Summoner '{summoner}' not found in match, only summoners "
        f"{all_participants} available")


def main():
    """Main function to download all desired matches of the summoner."""
    print("Welcome summoner!")
    if CROP_MATCHES:
        print("Returning cropped match data")
    else:
        print("Returning full data for all matches")
    print("")

    # Get user configuration
    config = get_config()
    summoners = get_summoners(config)
    region = get_region(config)
    queues = get_queues(config)
    print("")

    # API interface
    api_token = get_api_token()
    watcher = LolWatcher(api_token)

    # Iterate over all summoners
    for summoner in summoners:
        print(f"Retrieving data from summoner '{summoner[0]}'")
        try:
            summoner_id = watcher.summoner.by_name(region,
                                                   summoner[0])['accountId']
        except Exception as exc:
            print(f"WARNING: Cannot retrieve ID of summoner '{summoner[0]}': "
                  f"{str(exc)}")
            print("")
            continue
        matches_file = get_matches_filename(config, summoner[0])
        if os.path.isfile(matches_file):
            print(f"WARNING: Overwriting existing file {matches_file}")
            os.remove(matches_file)

        # Add summoner name to top of file
        with open(matches_file, 'a') as outfile:
            yaml.safe_dump([summoner[0]], outfile)

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
                print("")
                break
            try:
                match = watcher.match.by_id(region, matches[0]['gameId'])
            except Exception as exc:
                print(f"Retrieving matches failed: {str(exc)}")
                time.sleep(1.0)
                continue

            # Crop match data if desired
            if CROP_MATCHES:
                try:
                    match = get_summoner_stats(match, summoner)
                except ValueError as exc:
                    print(f"WARNING: {str(exc)}")
                    idx += 1
                    continue

            # Save file
            with open(matches_file, 'a') as outfile:
                yaml.safe_dump([match], outfile)
                print(f"Saved match {idx:5d} to '{matches_file}'")
            idx += 1


if __name__ == '__main__':
    main()
