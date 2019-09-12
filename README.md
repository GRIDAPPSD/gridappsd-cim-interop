# GridAPPS-D Sample Application

## Purpose

The purpose of this repository is to document the chosen way of registering and running applications within a 
GridAPPS-D deployment.

## Requirements

1. Docker ce version 17.12 or better.  You can install this via the docker_install_ubuntu.sh script.  (note for mint you will need to modify the file to work with xenial rather than ubuntu generically)

## Quick Start

The following procedure will use the already existing containers for the gridappsd sample application.

1. Clone the gridappsd-docker repository
    ```console
    git clone https://github.com/GRIDAPPSD/gridappsd-docker
    cd gridappsd-docker
    ```
1. Run the docker containers
    ```console
    ./run.sh
    ```
1. Once inside the container start gridappsd
    ```console
    ./run-gridappsd.sh
    ```
    
1. Open browser to http://localhost:8080 (follow instructions https://gridappsd.readthedocs.io/en/latest/using_gridappsd/index.html to run the application)
    
## Sample Application Layout

The following is the recommended structure for an applications working with gridappsd:

```console
.
├── README.md
├── requirements.txt
├── sample_app
│   └── runsample.py
└── sample_app.config
```

# IGNORE BELOW THIS!

1. Please clone the repository <https://github.com/GRIDAPPSD/gridappsd-docker> (refered to as gridappsd-docker repository) next to this repository (they should both have the same parent folder)

    ```console
    git clone -b develop https://github.com/temcdrm/gridappsd-docker
    git clone -b develop https://github.com/GRIDAPPSD/gridappsd-cim-interop
    ```

## Creating the sample-app application container

1.  From the command line execute the following commands to build the sample-app container

    ```console
    > cd gridappsd-cim-interop
    > docker build --network=host -t derms_app .
    ```

1.  Add the following to the gridappsd-docker/docker-compose.yml file

    ```` yaml
    dermsapp:
      image: derms_app
      depends_on: 
        gridappsd    
    ````

1.  Run the docker application 

    ```` console
    osboxes@osboxes> cd gridappsd-docker
    osboxes@osboxes> ./run.sh
    
    # you will now be inside the container, the following starts gridappsd
    
    gridappsd@f4ede7dacb7d:/gridappsd$ ./run-gridappsd.sh
    
    ````

Next to start the application through the viz follow the directions here: https://gridappsd.readthedocs.io/en/latest/using_gridappsd/index.html#start-gridapps-d-platform
