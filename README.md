# irbase

## Python3 setup on BMI cluster

Set up some enviroments variables for the venv:

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

## Visual Studio Code ##

Download and install Visual Studio Code from:

https://code.visualstudio.com/

Start Visual Studio Code and click Extentions (icon of four boxes on the left or type ctrl-shift-x) and search for and install the following extentions:
```
Remote-SSH
Python
```

## Making an SSH key on the cluster ##

I suggest making the SSH key on the cluster. You can do this by logging into the cluster and running
```
ssh-keygen
```
On the command line. Use the default location for the key: .ssh/id_rsa. I usually use an empty passphrase. You'll
download this key to your local machine, linking the computers together, in one of the next two sections
depending on your operating system.

## Setting up SSH on Windows for use by VC Code ##

You'll need install the OpenSSH client so that you can connect to the cluster. Follow the instructions here:

https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse#installing-openssh-from-the-settings-ui-on-windows-server-2019-or-windows-10-1809

Then open the Command Prompt (hit the windows key, type "cmd", and hit enter) and the make the .ssh directory:
```
mkdir .ssh
```
Then, start Visual Studio Code to edit the SSH config file
```
cd
cd .ssh
code config
```
And add the following lines, making sure to change *both* instances YOURUSERNAME to your cluster username, before saving the file:
```
Host *
    ServerAliveInterval 60
Host ssh cchmc
    HostName ssh.research.cchmc.org
    User YOURUSERNAME
Host bmiclusterp bmiclusterp2 cluster
    Hostname bmiclusterp.chmcres.cchmc.org
    User YOURUSERNAME
    ProxyCommand C:\Windows\System32\OpenSSH\ssh.exe -q ssh nc -w 180 %h %p
```
(the extra hope through ssh.research.cchmc.org means you'll be able to connect without having to use the VPN) then you
should be able to download the private key by running (in the .ssh directory):
```
scp cluster:.ssh/id_dsa .
```
Once it's downloaded, you should be able to run
```
ssh cluster
```
without having to enter your password.

## Setting up SSH on MacOSX/Linux for use by VC Code ##

Linux and MacOSX already have SSH installed so you only have to modify the config file. Edit ~/.ssh/config
(note this file might not already exists but that's ok) and add the following lines, making sure to change
*both* instances YOURUSERNAME to your cluster username, before saving the file:
```
Host *
    ServerAliveInterval 60
Host ssh cchmc
    HostName ssh.research.cchmc.org
    User YOURUSERNAME
Host bmiclusterp bmiclusterp2 cluster
    Hostname bmiclusterp.chmcres.cchmc.org
    User YOURUSERNAME
    ProxyCommand ssh -q ssh nc -w 180 %h %p
```
(the extra hope through ssh.research.cchmc.org means you'll be able to connect without having to use the VPN) then you
should be able to download the private key by running (in the .ssh directory):
```
scp cluster:.ssh/id_dsa ~/.ssh/
```
Once it's downloaded, you should be able to run
```
ssh cluster
```
without having to enter your password.

### Using Visual Studio Code ###

Now select Remote Explorer (icon of a monitor on the left) and you should be able to select "cluster" from the list to connect to the cluster.

More to come.

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
