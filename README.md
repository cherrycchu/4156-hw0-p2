# Search Query Expansion

## Virtual Environment Setup

### General Setup

```bash
# generic update
sudo apt-get update

# installing stuffs
sudo apt-get install git python-virtualenv python-dev

# tmux
sudo apt install tmux

# update .bashrc
### START COPY ###
export VISUAL=vim
export EDITOR="$VISUAL"
### END COPY ###

# update .bash_profile
### START COPY ###
if [ -f ~/.bashrc ]; then
  . ~/.bashrc
fi
### END COPY ###
```

### GitHub Setup

#### Git SSH

1. Generate ssh key on the VM: follow https://help.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
2. Add ssh key on VM to github: follow https://developer.github.com/v3/guides/managing-deploy-keys/#deploy-keys
    1. Copy the ssh key on VM to clipboard (~/.ssh/id_rsa.pub)
    2. Open the settings in this repo, find deploy key option, paste the ssh key there
3. Setup git config

```bash
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
git config --global core.editor "vim"
```

4. Clone this repo to the home directory of the VM using git ssh `git clone git@github.com:deka108/6111proj1.git`

Note that any pull / push requests should be done using git ssh instead of https

### Python and Virtual Environment Setup on VM

Note: let's generate requirements.txt whenever we install new package

```bash
# python
sudo apt-get install python3
sudo apt-get upgrade python3

# install python 3.7
# Follow https://linuxize.com/post/how-to-install-python-3-7-on-ubuntu-18-04/

# install miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh

# run installer for miniconda (agree with the options)
bash ~/miniconda.sh
source ~/.bashrc

# don't automatically run conda at initial
conda config --set auto_activate_base false
```

### Using Conda

Always **activate Conda Environment** whenever doing a project.

**Prerequisites:** Install python 3.7 and conda on local computer or VM

Perform the following steps on VM and local environment to create a new conda environment

```bash
# create virtualenv
conda create --name 6111 python=3.7

# Activate virtualenv (from the same directory as where the virtualenv files is located, usually at home directory)
conda activate 6111

# Install basic packages
conda install numpy pandas scikit-learn
pip install --upgrade google-api-python-client
conda install jupyter
conda install -c conda-forge python-dotenv

# add 6111 as one of the jupyter kernels
ipython kernel install --name 6111

# Deactivating virtualenv (do this if no longer working on a project or wish to change to different virtualenv)
conda deactivate

# During activated env - Generating env.yml (list of currently installed packages on conda) for reproducing conda environment
conda env export --no-builds > env[-env].yml
conda env export --no-builds > env-vm.yml # if on local vm
conda env export --no-builds > env-mac.yml # if on local mac

# During activate env - Updating an conda env from packages in env.yml (don't forget to activate the virtual env first)
conda env update --file env[-env].yml 

# During activated env - Generating requirements.txt
pip freeze > requirements.txt

# Creating a new conda environment based on existing env.yml (will install packages inside that)
conda env create -f [environment_name].yml
```
