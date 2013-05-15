pybabel extract -F babel.cfg -o messages.pot .
pybabel update -i messages.pot -d translations -l ko

