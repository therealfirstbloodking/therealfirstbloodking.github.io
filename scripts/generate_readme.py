#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import yaml
from scipy import stats

from __init__ import get_config, get_outfile, get_summoner_info


ALPHA = 0.05
PROB_BINOM = 0.1
PLOT_DIR = os.path.join('..', 'img')


def generate_readme(p_value, summoner, readme_path='../README.md',
                    readme_header='readme_header.md'):
    """Generate README."""
    with open(readme_header, 'r') as infile:
        readme_info = infile.read()

    # Save plot
    if not os.path.isdir(PLOT_DIR):
        os.makedirs(PLOT_DIR)
        print(f"Created '{PLOT_DIR}'")
    filename = summoner[0].replace(' ', '_') + '.png'
    plot_path = os.path.join(PLOT_DIR, filename)
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"Saved {plot_path}")
    readme_info += f'![First blood king]({plot_path})'

    # Text
    if p_value < ALPHA:
        readme_info += ('STILL THE FIRST BLOOD KING!!!\n'
                        '=============================\n\n\n')
    else:
        readme_info += ('Not first blood king anymore :-(\n'
                        '================================\n\n\n')
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    readme_info += f'Last updated: {now}\n'

    # Write README
    with open(readme_path, 'w') as outfile:
        outfile.write(readme_info)

    print(f"Wrote {readme_path}")


def get_summoner_stats(match, summoner):
    """Get only Summoner's stats for a certain match."""
    for participant_id in match['participantIdentities']:
        if participant_id['player']['summonerName'] in summoner:
            summoner_id = participant_id['participantId']
            break
    else:
        raise ValueError(f"Summoner '{summoner}' not found in match")
    for participant in match['participants']:
        if participant['participantId'] == summoner_id:
            return participant
    raise ValueError(f"Summoner '{summoner}' not found in match")


def is_match(match):
    """Check if match is counted as match."""
    return True


def is_first_blood(match):
    """Check if match counts as first blood."""
    return match['stats']['firstBloodKill']


def main():
    """Main function to analyze the stats of the Summoner."""
    config = get_config()
    (summoner, _, _) = get_summoner_info(config)
    infile = get_outfile(config, summoner[0])
    cached_file = infile.replace('.yml', '_only.yml')
    if not os.path.isfile(cached_file):
        print(f"Creating '{cached_file}' to cache Summoner only")
        with open(infile, 'r') as file_:
            matches = yaml.safe_load(file_)
            print(f"Loaded '{infile}'")
        matches_summoner_only = []
        for match in matches:
            summoner_stats = get_summoner_stats(match, summoner)
            matches_summoner_only.append(summoner_stats)
        with open(cached_file, 'w') as file_:
            yaml.safe_dump(matches_summoner_only, file_)
            print(f"Created cached file '{cached_file}'")
    else:
        print(f"Found cached file '{cached_file}'")
        with open(cached_file, 'r') as file_:
            matches_summoner_only = yaml.safe_load(file_)
            print(f"Loaded cached file '{cached_file}'")

    # Get number of matches and first bloods
    n_matches = 0
    n_first_bloods = 0
    for match in matches_summoner_only:
        if is_match(match):
            n_matches += 1
            if is_first_blood(match):
                n_first_bloods += 1
    print(f"Found {n_matches:5d} matches")
    print(f"Found {n_first_bloods:5d} first bloods")

    # Binomial test
    p_value = stats.binom_test(n_first_bloods, n=n_matches, p=PROB_BINOM,
                               alternative='greater')
    print(f"p value: {p_value:e}")

    # Plot
    x = np.arange(n_matches)
    y = stats.binom(n_matches, PROB_BINOM).pmf(x)
    plt.plot(x, y, label=f'H0: {summoner[0]} ist normaler Mensch')
    plt.axvline(n_first_bloods, color='r', label=summoner[0])
    plt.fill_between(x, 0.0, y, where=x <= n_first_bloods, alpha=0.5)
    plt.xlabel('Number of first bloods')
    plt.ylabel('Probability')
    plt.title("First blood king?")
    plt.legend()

    # Update README
    generate_readme(p_value, summoner)


if __name__ == '__main__':
    sns.set()
    main()
