from clld.web.assets import environment
from clldutils.path import Path

import clics


environment.append_path(
    Path(clics.__file__).parent.joinpath('static').as_posix(),
    url='/clics:static/')
environment.load_path = list(reversed(environment.load_path))
