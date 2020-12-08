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

## Setting up SSH on the cluster ##


## Visual Studio Code ##

Download and install Visual Studio Code from:

https://code.visualstudio.com/

### Windows ###

First, you'll need install an SSH client so that you can connect to the cluster. Follow the instructions here:

https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse#installing-openssh-from-the-settings-ui-on-windows-server-2019-or-windows-10-1809

Then open the Command Prompt (hit the windows key, type "cmd", and hit enter). Then make the make the .ssh directory:
```
mkdir .ssh
```
Then, start Visual Studio Code to edit the SSH config file
```
cd .ssh
code config
```
And add the following lines, making sure to change YOURUSERNAME to your cluster username, before saving the file:
```
Host bmiclusterp bmiclusterp2 cluster
    Hostname bmiclusterp.chmcres.cchmc.org
    User YOURUSERNAME
```
then you should be able to download the private key by running (in the .ssh directory):
```
scp cluster:.ssh/id_dsa .
```
Once it's downloaded, you should be able to run
```
ssh cluster
```
without having to enter your password.

## Getting and using the repository

To set up git, on the command line run:
```
git config --global user.name "Firstname Lastname"
git config --global user.email emailaddress@something.com
git config --global credential.helper store
```
Then in github you can click on your profile picture and select settings Settings. Then
click Developer Settings on the lower left and then Personal access tokens. From there
you can Generate a new token. Give it a descriptive and you probably only need "repo"
to be in the scope of the token. Copy the personal access token, you'll be using it as your password in a second.

Then from the command like, you can do:
```
cd ~
git clone https://github.com/roskinlab/irbase.git
```
and enter in your github username and the personal access token as your password (be sure to use all lowercase for your git username).

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
