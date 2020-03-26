#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import yaml
from scipy import stats

from __init__ import (DATA_FILE, MATCHES_PREFIX, get_config, get_data_dir,
                      get_plot_dir)


ALPHA = 0.05
PROB_BINOM = 0.1


def binomial_test(n_first_bloods, n_matches):
    """Get p value of left-sided binomial test."""
    p_value = stats.binom_test(n_first_bloods, n=n_matches, p=PROB_BINOM,
                               alternative='greater')
    return p_value


def get_input_files(config):
    """Get all input files."""
    data_dir = get_data_dir(config)
    pattern = f'{MATCHES_PREFIX}*.yml'
    return glob.glob(os.path.join(data_dir, pattern))


def plot_distribution(summoner, n_first_bloods, n_matches, p_value, config):
    """Create distribution plot."""
    x = np.arange(n_matches)
    y = stats.binom(n_matches, PROB_BINOM).pmf(x)

    # Create plot
    plt.plot(x, y, label=f'H0: $B({n_matches:d}, {PROB_BINOM:.2f})$')
    plt.axvline(n_first_bloods, color='r',
                label=f'{summoner}: {n_first_bloods:d} first blood kills')
    plt.fill_between(x, 0.0, y, where=x <= n_first_bloods, alpha=0.5)
    plt.xlabel('Number of first bloods')
    plt.ylabel('Probability')
    plt.xlim(0.0, 4.0 * PROB_BINOM * n_matches)
    plt.title("Distribution of first blood kills")
    plt.legend(loc='upper right')

    # Save plot
    plot_dir_abs = get_plot_dir(config, absolute=True)
    plot_dir_rel = get_plot_dir(config, absolute=False)
    filename = summoner.replace(' ', '_') + '.png'
    plot_path_abs = os.path.join(plot_dir_abs, filename)
    plot_path_rel = os.path.join(plot_dir_rel, filename)
    plt.savefig(plot_path_abs, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved {plot_path_abs}")
    return plot_path_rel


def is_match(match):
    """Check if match is counted as match."""
    return True


def is_first_blood(match):
    """Check if match counts as first blood."""
    return match['stats']['firstBloodKill']


def main():
    """Main function to analyze the stats of the Summoner."""
    config = get_config()
    input_files = get_input_files(config)
    data_dir = get_data_dir(config)
    data_file = os.path.join(data_dir, DATA_FILE)
    if os.path.isfile(data_file):
        print(f"WARNING: Overwriting existing file {data_file}")
        print("")
        os.remove(data_file)

    # Output dict
    data_dict = {}
    metadata = {
        'alpha': ALPHA,
        'p_binom': PROB_BINOM,
    }
    data_dict['metadata'] = metadata

    # Iterate over input files
    data_dict['summoners'] = {}
    for input_file in input_files:
        print(f"Reading {input_file}")
        with open(input_file, 'r') as infile:
            matches = yaml.safe_load(infile)
        summoner = matches.pop(0)
        print(f"Found summoner '{summoner}'")

        # Get number of matches and first bloods
        n_matches = 0
        n_first_bloods = 0
        for match in matches:
            if is_match(match):
                n_matches += 1
                if is_first_blood(match):
                    n_first_bloods += 1
        ratio = float(n_first_bloods) / float(n_matches)

        # Binomial test
        p_value = float(binomial_test(n_first_bloods, n_matches))

        # Create plot
        plot_path = plot_distribution(summoner, n_first_bloods, n_matches,
                                      p_value, config)

        # Write information
        print(f"Found {n_matches:5d} matches")
        print(f"Found {n_first_bloods:5d} first bloods")
        print(f"First blood ratio: {100.0 * ratio:.2f}%")
        print("")

        # Write file
        data_dict['summoners'][summoner] = {
            'n_matches': n_matches,
            'n_first_bloods': n_first_bloods,
            'first_blood_ratio': ratio,
            'p_value': p_value,
            'distribution_plot': plot_path,
        }

    # Save file
    with open(data_file, 'a') as outfile:
        yaml.safe_dump(data_dict, outfile)
    print(f"Wrote {data_file}")


if __name__ == '__main__':
    sns.set()
    main()
