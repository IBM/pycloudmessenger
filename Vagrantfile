# -*- mode: ruby -*-
# vi: set ft=ruby :

#Vagrant::DEFAULT_SERVER_URL.replace('https://vagrantcloud.com')

$machine_addr = "192.168.56.111"

$machine_cap  = "90"
$machine_cpus = "2"
$machine_name = "ubuntu-pycloud"
$machine_ram  = "4096"
$machine_ram  = "8192"


$provision_root = <<'SCRIPT_ROOT'

#echo "fetch, install docker ce"
apt-get update
apt-get install -y apt-transport-https ca-certificates curl software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository  "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

apt-get install -y docker-ce
usermod -aG docker vagrant

apt-get upgrade -y
apt-get install -y coreutils build-essential make libffi-dev libc6-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev python-openssl zlib1g-dev libssl-dev libbz2-dev jq zip

SCRIPT_ROOT


$provision_user = <<'SCRIPT_USER'

# Adds github.com to known hosts
if [ ! -n "$(grep "^github.com " ~/.ssh/known_hosts)" ]; then
    ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts;
fi

cd /vagrant

echo "Adding local pip to the path"
export PATH=${HOME}/.local/bin/:${PATH}
mkdir -p ${HOME}/.local/bin

echo "Installing pyenv"
#git clone https://github.com/pyenv/pyenv.git ~/.pyenv
curl https://pyenv.run | bash
export PATH="~/.pyenv/bin:$PATH"
pyenv install 3.6.13
pyenv global 3.6.13
eval "$(pyenv init --path)"
#pyenv virtualenv 3.6.13 36
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r test_requirements.txt

pyenv install 3.9.0
pyenv global 3.9.0
eval "$(pyenv init --path)"
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r test_requirements.txt

#Set up some niceities in the shell
cat <<'EOF_BASHRC' >> $HOME/.bashrc
# http://stackoverflow.com/questions/9457233/unlimited-bash-history
export HISTFILESIZE=
export HISTSIZE=
export HISTTIMEFORMAT="[%F %T] "
export HISTFILE=/vagrant/bash_history
PROMPT_COMMAND="history -a; $PROMPT_COMMAND"

export PATH=$HOME/.local/bin:$PATH
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"

alias ls='ls --color=auto'
alias grep='grep --color=auto'
export PS1='\[\e]0;\u@\h: \w\a\]\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\n$ '

cd /vagrant

EOF_BASHRC

cat <<'EOF_VIM' > $HOME/.vimrc
"colour scheme for dark background
colorscheme ron

set hlsearch
set showmode
set showmatch
set noautoindent
set esckeys

set scrolloff=3

" configure expanding of tabs for various file types
au BufRead,BufNewFile *.py set autoindent
au BufRead,BufNewFile *.py set expandtab
au BufRead,BufNewFile *.py set tabstop=4
au BufRead,BufNewFile *.py set softtabstop=4
au BufRead,BufNewFile *.py set shiftwidth=4

" configure expanding of tabs for various file types
au BufRead,BufNewFile *.yaml set autoindent
au BufRead,BufNewFile *.yaml set expandtab
au BufRead,BufNewFile *.yaml set shiftwidth=2
au BufRead,BufNewFile *.yaml set softtabstop=2
au BufRead,BufNewFile *.yaml set tabstop=2

EOF_VIM

SCRIPT_USER


Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"

  config.vm.provision :shell, inline: $provision_root
  config.vm.provision :shell, privileged: false, inline: $provision_user

  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--name", $machine_name]
    vb.customize ["modifyvm", :id, "--cpus", $machine_cpus]
    vb.customize ["modifyvm", :id, "--cpuexecutioncap", $machine_cap]
    vb.customize ["modifyvm", :id, "--memory", $machine_ram]
  end

  if Vagrant.has_plugin?("vagrant-vbguest")
    config.vbguest.auto_update = true
  end

  # Copy your .gitconfig file so that your git credentials are correct
  if File.exists?(File.expand_path("~/.gitconfig"))
    config.vm.provision "file", source: "~/.gitconfig", destination: "~/.gitconfig"
  end

  # Copy the ssh keys into the vm
  if File.exists?(File.expand_path("~/.ssh/id_rsa"))
    config.vm.provision "file", source: "~/.ssh/id_rsa", destination: "~/.ssh/id_rsa"
  end

  if File.exists?(File.expand_path("~/.ssh/id_rsa.pub"))
    config.vm.provision "file", source: "~/.ssh/id_rsa.pub", destination: "~/.ssh/id_rsa.pub"
  end

  config.vm.hostname = $machine_name
  config.vm.network :private_network, ip: $machine_addr
end
