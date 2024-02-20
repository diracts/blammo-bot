#!/bin/bash

# Test that the user has python3 installed. If not, return an error. 
if ! [ -x "$(command -v python3)" ]; then
    echo "Error: python3 is not installed." >&2
    exit 1
else
    echo "Found existing python3 installation"
fi

# Test that the user has pip installed. If not, return an error.
if ! [ -x "$(command -v pip)" ]; then
    echo "Error: pip is not installed." >&2
    exit 1
else
    echo "Found existing pip installation"
fi

# Loop to check the user's input
while true; do
    read -p "Do you have a virtual environment you would like to use? (y/n) " yn
    case $yn in
        [Yy]* ) use_virtual_env="y"; break;;
        [Nn]* ) use_virtual_env="n"; break;;
        * ) echo "Please answer y or n.";;
    esac
done

# If the user has a virtual environment, ask for the path to the virtual environment
if [ $use_virtual_env == "y" ]; then
    echo "Please enter the path to the virtual environment"
    read virtual_env_path
    source $virtual_env_path/bin/activate
else
    # If the user does not have a virtual environment, create one
    echo "Please enter the name of the virtual environment you would like to create"
    read virtual_env_name
    python3 -m venv $virtual_env_name
    source $virtual_env_name/bin/activate
fi

# Ask whether you would like to install all the packages or select them individually
while true; do
    read -p "Would you like to install all the required packages? (y/n) " yn
    case $yn in
        [Yy]* ) install_all="y"; break;;
        [Nn]* ) install_all="n"; break;;
        * ) echo "Please answer y or n.";;
    esac
done

# Create a function to check if a python package is installed
#   if not installed, ask whether to install it and install it
#   if installed, print that it is already installed

function check_install {
    if python -c "import $1" &> /dev/null; then
        echo "$1 is already installed"
    else
        echo "$1 is not installed"
        echo "Would you like to install $1? (y/n)"
        read install_package
        if [ $install_package == "y" ]; then
            pip install $1
        fi
    fi
}

# TODO: Make sure this installs into the right venv
# TODO: If new venv is in this repo, append rel path to .gitignore

# Create a list of required python packages
# TODO: remove packages that are default in python
required_packages=(
    "numpy"
    "pandas"
    "matplotlib"
    "seaborn"
    "scikit-learn"
    "jupyter"
    # "ipykernel"
    # "ipywidgets"
    # "plotly"
    "urllib3"
    "requests"
    "asyncio"
    "subprocess"
    "datetime"
    "time"
    "json"
    "datetime"
    "signal"
    "pathlib"
    "difflib"
)

if [ $install_all == "y" ]; then
    # pip install every package in one command
    pip install "${required_packages[@]}"
else
    # Loop through the list of required packages and check if they are installed
    for package in "${required_packages[@]}"; do
        check_install $package
    done
fi

# Install fork of PythonTwitchBotFramework
echo Installing required package: PythonTwitchBotFramework fork
pip install https://github.com/diracts/PythonTwitchBotFramework.git

# Adding the virtual environment to the .gitignore
if [ $use_virtual_env == "n" ]; then
    echo "Adding the virtual environment to the .gitignore"
    echo $virtual_env_name >> .gitignore
else
    echo "If your virtual environment is in this directory, make sure to add it to the .gitignore"
fi

