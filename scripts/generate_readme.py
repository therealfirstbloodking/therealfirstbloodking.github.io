#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime

import yaml

from __init__ import DATA_FILE, get_config, get_data_dir


def main():
    """Main function to analyze the stats of the Summoner."""
    config = get_config()
    data_dir = get_data_dir(config)
    data_file = os.path.join(data_dir, DATA_FILE)

    # Read file
    with open(data_file, 'r') as infile:
        data_dict = yaml.safe_load(infile)

    # Write header
    with open('readme_header.md', 'r') as infile:
        readme = infile.read()

    # Write plots for individual summoners
    metadata = data_dict['metadata']
    for (summoner, summoner_data) in data_dict['summoners'].items():
        readme += summoner + '\n'
        readme += '-' * len(summoner) + '\n\n'

        # Plot
        readme += f"![{summoner}]({summoner_data['distribution_plot']})\n\n"

        # Description
        if summoner_data['p_value'] < metadata['alpha']:
            readme += '**FIRST BLOOD KING!!!**\n\n'
        else:
            readme += '**not first blood king :-(**\n\n'
        readme += (f"{summoner} has {summoner_data['n_first_bloods']:d} "
                   f"first bloods in {summoner_data['n_matches']:d} games. "
                   f"Assuming a binomial distribution with parameters ``p = "
                   f"{metadata['p_binom']:.2f}`` and ``n = "
                   f"{summoner_data['n_matches']:d}`` as null hypothesis, "
                   f"the corresponding p value is ``p = "
                   f"{summoner_data['p_value']:e}``.\n\n\n")

    # Finalize
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    readme += f'Last updated: {now} UTC'

    # Write
    readme_path = os.path.abspath(os.path.join('..', 'README.md'))
    with open(readme_path, 'w') as outfile:
        outfile.write(readme)
    print(f"Wrote {readme_path}")


if __name__ == '__main__':
    main()
