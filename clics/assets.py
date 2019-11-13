import pathlib

from clld.web.assets import environment

import clics


environment.append_path(
    str(pathlib.Path(clics.__file__).parent.joinpath('static')),
    url='/clics:static/')
environment.load_path = list(reversed(environment.load_path))
