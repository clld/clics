"""

"""
import pathlib
import subprocess
import contextlib
import argparse

from clldutils import db
import transaction
from clld.scripts.util import ExistingConfig, SessionContext, get_env_and_settings
from cldfbench.cli_util import add_catalog_spec
from cldfcatalog import Config, Catalog
from pyconcepticon import Concepticon

import clics
from clics.scripts.initializedb import prime_cache, main
from clics import models

PROJECT_DIR = pathlib.Path(clics.__file__).parent.parent


def register(parser):  # pragma: no cover
    add_catalog_spec(parser, 'concepticon')
    parser.add_argument(
        "--config-uri",
        action=ExistingConfig,
        help="ini file providing app config",
        default=str(PROJECT_DIR / 'development.ini'))
    parser.add_argument(
        '--doi',
        default=None,
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=False,
    )
    parser.add_argument(
        '--prime-cache-only',
        action='store_true',
        default=False,
    )
    parser.add_argument(
        '--test',
        action='store_true',
        default=False,
        help=argparse.SUPPRESS,
    )


@contextlib.contextmanager
def dryrun_ini(db_):  # pragma: no cover
    p = PROJECT_DIR / 'dryrun.ini'
    p.write_text("""\
[app: main]
use = egg:clics
sqlalchemy.url = {0}

[server: main]
use = egg:waitress
host = 0.0.0.0
port = 6543
""".format(db_), encoding='utf8')
    yield p
    p.unlink()


def run(args):  # pragma: no cover
    args.env, settings = get_env_and_settings(args.config_uri)

    if not args.concepticon:
        try:
            args.concepticon = Config.from_file().get_clone('concepticon')
        except KeyError:  # pragma: no cover
            raise ValueError

    if args.dry_run:
        settings[db.DB.settings_key] += '.dryrun'
        db_cls = db.TempDB
    else:
        db_cls = db.FreshDB  # pragma: no cover

    with Catalog(args.concepticon, args.concepticon_version) as cat:
        args.concepticon = Concepticon(cat.dir)
        with db_cls.from_settings(settings, log=args.log) as db_:
            with SessionContext(settings) as sess:
                if not args.prime_cache_only:
                    with transaction.manager:
                        main(args)
                with transaction.manager:
                    prime_cache(args)
                if args.test:
                    with transaction.manager:
                        #assert len(sess().query(models.Conceptlist).all()) == 2
                        pass
            if args.dry_run and not args.test:  # pragma: no cover
                with dryrun_ini(db_) as config:
                    subprocess.check_call(
                        ['pytest', '--appini', str(config)], cwd=str(PROJECT_DIR))
