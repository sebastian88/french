### Setup a virtual environment (recommended)

Create an isolated environment at the root of the project and activate it:

```sh
python3 -m venv venv
```

Activate the venv:

```sh
source venv/bin/activate
```

### Install dependencies

```sh
pip install mysql-connector-python
pip install flask
pip install -U flask-cors
```

### Run

```sh
python main.py
```

### Errors

If you get `No module named 'urllib3.packages.six.moves'`
run
```
pip install requests --upgrade

pip install urllib3 --upgrade
```
see https://stackoverflow.com/questions/78163280/no-module-named-urllib3-packages-six-moves