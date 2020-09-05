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
## Getting and using the repository

To set up git, on the command line run:

git config --global user.name "Firstname Lastname"
git config --global user.email emailaddress@something.com
git config --global credential.helper store

Then in github you can click on your profile picture and select settings Settings. Then
click Developer Settings on the lower left and then Personal access tokens. From there
you can Generate a new token. Give it a descriptive and you probably only need "repo"
to be in the scope of the token. Copy the personal access token, you'll be using it as your password in a second.

Then from the command like, you can do:
```
cd ~
git clone https://github.com/roskinlab/irbase.git
```
and enter in your github username and the personal access token as your password.

Then you will need to tell python to look there when you do an import:
```
export PYTHONPATH=$HOME/irbase:$PYTHONPATH
```
Add the above command to your ~/.bashrc file so that setup everytime you loging.

Then you should be able to do:
```
source ~/envs/cluster/bin/activate
python
import roskinlib
```
