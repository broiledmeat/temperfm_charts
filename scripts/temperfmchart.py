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
    import temperfm
    import temperfm_charts

    args = docopt(__doc__, version=f'TemperFM Charts {temperfm_charts.__version__}, TemperFM {temperfm.__version__}')

    try:
        temperfm.load_config(args['--config'] or temperfm.DEFAULT_CONFIG_PATH)

        if args['weekly']:
            username = args['<username>']
            filepath = args.get('<filepath>') or f'weekly_{username}.svg'
            kwargs = {}

            try:
                kwargs['limit'] = int(args['<weeks>'])
            except (TypeError, ValueError):
                pass

            report = temperfm.get_user_weekly_artists(username, **kwargs)
            temperfm_charts.render_user_weekly_artists(report, filepath)
    except RuntimeError as e:
        sys.stderr.write(f'{e}\n')
        exit(1)


if __name__ == '__main__':
    main()
