# irbase

## Python3 setup on BMI cluster

Set up some enviroments variables for the vevent:

```
module load libffi         # you'll want this for using pandas, etc.
module load python3/3.7.1  # my "prefered" version of python
```

Then create a new venv:

```
cd ~
mkdir envs
python -m venv ~/envs/cluster   # NOTE: use python instead of python3
```

Some packages (notable pandas) needs the libffi module loaded. To get this to happen when everyou activate this venv, edit ~/envs/cluster/bin/activate and add
```
module load libffi
```
to the end of that file.

Now you can activate it using:

```
source ~/envs/cluster/bin/activate
```

and install some common packages:

```
proxy_on    # to let you download packages from the internet
pip install --upgrade pyarrow pip fastavro biopython scipy numpy pandas scikit-learn
```
