## Driving The Engraver

Once all the mechanical parts of the system are put together, you need to be
able to send instructions. This basic collection of files will allow you to do
that. Bearing in mind several factors.

1. Running on a Raspberry PI is not necessarily the _best_ way to put together a
   time sensitive device.
1. This system is intended to be simple and easy to use, but you will have to
   set some numbers - such as the pins you have wired your components to.
1. Some of the libraries used may change under the hood - they are all respected
   OpenSource projects, but if something falls apart then so be it.

### Getting going

The first thing to do, is to set up a virtual python environment to run from. To
do that, if you are _not_ running an ubuntu based system, you can run
```
python3 -m venv /path/to/venv
```

If you _are_ running an ubuntu based system (e.g. doing dev on WSL) you are
going to have to take some extra steps, as the `ensurepip` module is missing.

```
python3 -m venv /path/to/venv --without-pip
wget https://bootstrap.pypa.io/get-pip.py
source /path/to/venv/activate.sh
python get-pip.py
```

Once you have a virtual environment up and running, and have pip installed in
it, you can install dependencies with
```
pip install -r requirements.txt
```

### Running Tests
If you are doing dev work, and want to test functionality, make sure you are in
the `driver-files` folder and run the `pytest` command to run all tests. Full
pytest configuration can be found in `driver-files/pytest.ini`.

### Configuring the pins you've wired
Depending on the accessories you have connected to your device, and the exact device
you are running with, you are going to want to define your own pin numbers for the 
various aspects of the laser. For ease of use, you can define a `.ini` file and provide 
it as an argument to the laser initialisation. Or you can can adjust the `default_pins.ini`
file in your local setup. All sections are required for the engraver to function correctly.
