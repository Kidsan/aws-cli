# AWS Manager

This is a wrapper on the python boto3 client that allows management of AWS resources via the cli.
Note: the passwd.txt file contains the username and password for the application, the same username and password can be used to access the AWS Console. The AWS account id is 507951548029.

## Installation

Dependencies used are recorded in the requirements.txt
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the dependencies.

```bash
python -m pip install -r requirements.txt # Linux
py -m pip install -r requirements.txt # Windows
```

## Usage
The application is started by running the main.py script
```bash
python main.py
```
A passwd.txt file must be placed in the project root to ensure the authentication process works. The application will exit if a valid passwd.txt file is not found, or if the passwd file does not meet the required spec (tab separated values, 4 per line: username, password, key id, secret access key)

### Menus
On login, the (aws) screen is displayed. This screen allows us navigate to any other screen:

1. ec2
2. s3
3. cloudwatch
4. autoscaling
5. ebs

To navigate to a screen, type its name (lowercase) and press enter.

On any screen, type `?` and press enter to list available commands

You can find a description of a command by typing `help <command-name>`

When being prompted for input, in most cases you can cancel by leaving the option blank.

You can exit from any screen by typing `exit` and pressing enter

You can go back from a screen to the main navigation screen by typing `back` and pressing enter
