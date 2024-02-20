#!/bin/bash

# Ask whether the user already has a virtual environment they would like to use
echo "Do you have a virtual environment you would like to use? (y/n)"
read use_virtual_env

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

# Loop through the list of required packages and check if they are installed
for package in "${required_packages[@]}"; do
    check_install $package
done

# Install fork of PythonTwitchBotFramework
pip install https://github.com/diracts/PythonTwitchBotFramework.git
