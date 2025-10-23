# CS261 Group 42 - 2024/2025
## Traffic Wizard
Welcome to Traffic Wizard! A program designed to simulate traffic flows at a junction and evaluate the results.

Additional notes of this repository owner: This was a group project created between 6 students. My role within this was the production of the simulation logic and code, this includes the running of the simulation as well as all of the prepatory work after error validation from the entry form.

### Deploying the Traffic Wizard
The traffic wizard is mostly self contained, however there are some things that need to be kept in mind when running it. 

1. When the code is run, it attempts to save the results of the traffic simulation in a folder called data, under data/data.db in the same directory as app.pex. To avoid conflicts, it is recommended that the user installs the application within a designated folder.

**Warning:** No checks are performed to ensure that the database has not been moved or deleted. If you do move the database, or if the database is saved in a shared location, please ensure all users are aware of this. 

2. The execute the code python 3.12 is required to be installed.
    - For non-techical users, it is recommended to have python 3.12 installed as the base python installation and to add python to the system path.
    - For more advanced users, it is recommended to either create a virtual environment with python 3.12 (no additional dependencies need to be installed). Ensure the virtual environment is active before running the code.


### Common Issues and troubleshooting:
- Connetion already running:
    This error can occur when you have the application already running or another instance of the application running 

- Database in use related errors: 

    In the event that there is an issue connecting to a database, such as multiple users attempting to connect at once or the connection unexpectedly fails, you can force the connection to close by restartin th application.


#### Linux
Select the application (penguinapp.pex) and assign the appropriate permissions
    
    > chmod +x penguinapp.pex # and then execute the file using 
    > ./penguinapp.pex. 

#### Windows
Run cmd as administrator and navigate to the installation location of winapp.pex. Execute the file using the command 
    > python winapp.pex

#### Macos
Open the console and navigate to macapp.pex. Execute the code by running:

    > python macapp.pex


## Development of the Traffic Wizard
### Creating a pex file

The command to create a pex file is:

    > pex -r requirements.txt . (optional: --platform PEP508\_environment-marker)   -o appname.pex --entry-point src.app

and run from the project root. When run without an environment:

    > pex -r requirements.txt . -o appname.pex --entry-point src.app

will default to the system it is being executed on.

### Accessing Documentation
To see the code documentation, navigate to docs/_build/index.html and open it in your browser
