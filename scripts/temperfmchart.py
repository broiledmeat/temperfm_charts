#!/usr/bin/env python3
"""TemperFM Charts

Usage:
  temperfmchart weekly <username> <weeks> [<filepath>] [--config=<path>]
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
    from temperfm_charts import __version__
    from temperfm import config, __version__ as __temperfm_version__

    args = docopt(__doc__, version=f'TemperFM Charts {__version__}, TemperFM {__temperfm_version__}')

    try:
        config.load(args['--config'])

        if args['weekly']:
            from temperfm import get_user_weekly_artists
            from temperfm_charts import render_user_weekly_artists

            username = args['<username>']
            filepath = args.get('<filepath>') or f'weekly_{username}.svg'
            kwargs = {}

            try:
                kwargs['limit'] = int(args['<weeks>'])
            except (TypeError, ValueError):
                pass

            report = get_user_weekly_artists(username, **kwargs)
            render_user_weekly_artists(report, filepath)
    except RuntimeError as e:
        sys.stderr.write(f'{e}\n')
        exit(1)


if __name__ == '__main__':
    main()
