flask-plate
===========

This is yet another boiler plate for flask, with bootstrap, redis &amp; formencode.

### Get Started

1. Install Redis & Run server
    
    http://redis.io

1. Install latest formencode from Github
    <pre>
    git clone git://github.com/formencode/formencode.git
    cd formencode
    python setup.py install
    </pre>

1. Clone flask-plate from Github.
    <pre>git clone https://github.com/haje01/flask-plate.git</pre>

1. Rename 'flask-plate' folder as your project name, and cd into it.

1. Install required python modules. ( Make virtual environment beforehand, if you want to )
    <pre>pip install -r requirements.txt</pre>

1. Find 'myapp's in the following files and change it into your own app's name.
    <pre>
        ./admin
        ./application.py
        ./myapp/config.py
        ./myapp/util.py
        ./myapp.uwsgi.xml
        ./myapp  (change folder name)
    </pre>

1. Run application, then test 'http://localhost:8000' with you browser.
    <pre>python application.py</pre>

1. If everything goes well, remove .git folder and init new repository for your project.

1. Edit as your own!

### Unittest

To unittest your application, modify `tests.py` and run it. You can override settings by edit `tests.cfg` file.


### Documentation by Sphinx

If you want to use Sphinx as document tool, 

1. download latest Sphinx source and install (Note: current PIP version(1.2b) has timezone error).
    <pre>
        wget https://bitbucket.org/birkenfeld/sphinx/get/default.zip
        python setup.py build
        python setup.py install
    </pre>

2. Move into `docs/` folder and init sphinx document root.
    <pre>
        sphinx-quickstart
    </pre>
    
3. If you have more than one language to support, make locale folder in `translations/` folder:
    <pre>
        mkdir -p translations/ko
    </pre>

    Then extract message strings into `_build/locale` by:
    <pre>
        make gettext
    </pre>

    And add `locale_dirs = ['translations']` to the end of `conf.py`

    Init .po files by `docs/babel-init`. After translations is done, compile them by `docs/babel-compile`.

### Command Line Completion

In order to activate admin script's tab completion:

1. If you are using MacOSX, upgrade to bash 4.2 & install bash-completion.

    http://techscienceinterest.blogspot.kr/2010/05/change-to-new-bash-shell-41-for-mac-os.html

    http://blog.jeffterrace.com/2012/09/bash-completion-for-mac-os-x.html

1.  Admin Command line Completion

    https://pypi.python.org/pypi/argcomplete#global-completion

