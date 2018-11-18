# Python hackathon
This documents contains basic explanation of implementation part.

# Solve the challenge
Firstly, clone this project:

``` shell
git clone <path_to_this_repo>
```

Then make a fresh [virtualenv](https://virtualenv.pypa.io/en/stable/)
and activate it. After that, install all required modules into active
virtualenv using:

``` shell
cd <dir_where_this_repo_is_cloned>
pip install -r requirements.txt
```

Then run the proposed solution with:

``` shell
python3 run_solution.py
```

Now run the framework part to start getting data from it:

``` shell
python3 run_framework.py
```

Visualization is by default available at
[http://localhost:8000/viz.html](http://localhost:8000/viz.html). All
these steps are also available as single script `run.py` that can be
run using:

``` shell
python3 run.py
```

or

``` shell
./run.py
```

*This script will run solution then framework and as the very last
step it will open your default system browser at visualization page.*

**All the available framework options are placed and explained in
params.conf**

**Before you start working on your solution consider the proposed
solution architecture.**

**Proposed solution as well as framework requires Python 3.**

## Typhoon framework
Typhoon framework is given as a Python script that could be run using:

``` shell
./run_framework.py
```

Or:

``` shell
python run_framework.py
```

Framework starts emitting data in the form of `DataMessage`
(`DataMessage` alongside with other offered utilities is placed in the
`utils` module) after time lapse specified in `params.conf`.

## Proposed solution
Communication between Typhoon framework and the solution is abstracted
through the `Control` class from `utils` module. Control class has
`get_data` and `push_results`. First method returns Python generator
that produces data sent by the framework encapsulated into
`DataMessage` objects. Second is aimed to send data back to the
Typhoon framework when it is ready, data that is sent should be
encapsulated into `ResultsMessage` object. Proposed solution that
depicts usage of the `Control` class is given below
(`hackathon/solution/solution.py`):

``` python
def worker(msg: DataMessage) -> ResultsMessage:
    """TODO: This function should be implemented by contestants."""

    # Dummy result is returned in every cycle here
    return ResultsMessage(data_msg=msg,
                          load_one=True,
                          load_two=True,
                          load_three=True,
                          power_reference=0.0,
                          pv_mode=PVMode.ON)


def run(args) -> None:
    prepare_dot_dir()
    config_outs(args, 'solution')

    cntrl = Control()

    for data in cntrl.get_data():
        cntrl.push_results(worker(data))
```

One can run proposed solution using:

``` shell
./run_solution.py
```

Or:

``` shell
python run_solution.py
```
