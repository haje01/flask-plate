flask-plate
===========

This is yet another boiler plate for flask, with bootstrap, redis &amp; formencode.

### Get Started

1. Clone from Github.
    <pre>git clone https://github.com/haje01/flask-plate.git</pre>

1. Rename 'flask-plate' folder as your project name, and cd into it.

1. Install required python modules.
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

1. Run application, then test 'localhost:8000' with you browser.
    <pre>python application.py</pre>

1. If everything goes well, remove .git folder and init new repository for your project.

1. Edit as your own!

### Tips

In order to activate admin script's tab completion:

1. If you are using MacOSX, upgrade to bash 4.2 & install bash-completion.
    http://blog.jeffterrace.com/2012/09/bash-completion-for-mac-os-x.html
    http://techscienceinterest.blogspot.kr/2010/05/change-to-new-bash-shell-41-for-mac-os.html

1. After argcomplete installed by requirements.txt, activate it globally.
    https://pypi.python.org/pypi/argcomplete#global-completion

