import os
from myapp import default_config

def make_config(app=None):
    if app is not None:
        cfg = app.config
    else:
        from flask.config import Config
        root_path = os.path.dirname(__file__).rsplit('/', 1)[0]
        cfg = Config(root_path)

    # customize config here
    cfg.from_object(default_config)
    cfg.from_pyfile('myapp.cfg', silent=True)
    cfg['BABEL_DEFAULT_LOCALE'] = cfg['LANG']
    return cfg
