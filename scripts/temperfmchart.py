#!/usr/bin/env python3
"""TemperFM Charts

Usage:
  temperfmchart weekly <username> <weeks> [<filepath>] --key=<key> [--profile=<profile>] [--log=<log>] [--cache=<cache>]
  temperfmchart (-h | --help)
  temperfmchart --version

Options:

  --config=<path>  Config file to use
  -h, --help       Show this screen
  --version        Show version
"""

import os
import sys


sys.path.remove(os.path.dirname(__file__))


def main():
    from docopt import docopt
    import temperfm
    from temperfm import TemperFm
    from temperfm.log import Logger
    from temperfm.profile import Profile
    from temperfm.lastfm import LastFm, LastFmCache
    import temperfm_charts

    default_profile_path = os.path.join(os.path.dirname(temperfm.__file__), 'resources/default_profile.json')
    default_cache_path = os.path.expanduser('~/.temperfm/cache.sqlite')
    default_log_path = os.path.expanduser('~/.temperfm/activity.log')

    args = docopt(__doc__, version=f'TemperFM Charts {temperfm_charts.__version__}, TemperFM {temperfm.__version__}')

    try:
        logger = Logger(args['--log'] or default_log_path)
        profile = Profile.load(args['--profile'] or default_profile_path)
        cache = LastFmCache(args['--cache'] or default_cache_path)
        lastfm = LastFm(args['--key'], logger, cache)
        temperfm = TemperFm(logger, profile, lastfm)

        if args['weekly']:
            username = args['<username>']
            filepath = args.get('<filepath>') or f'weekly_{username}.svg'
            weeks = int(args['<weeks>'])

            report = temperfm.get_user_weekly_artists(username, weeks)
            temperfm_charts.render_user_weekly_artists(report, filepath)
    except RuntimeError as e:
        sys.stderr.write(f'{e}\n')
        exit(1)


if __name__ == '__main__':
    main()
