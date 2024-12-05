# Build instructions
Ensure you have the following installed on your machine. Refer to 3rd-party documentation for each technology regarding installation steps:
- Python
- Pip
- Docker

## How to run the different parts of the solution. 

1. Rabbit MQ
	- Ensure Docker is installed and docker is accessible from your terminal 
	- Cd into client directory
	- Run docker-compose up
	- If docker is installed, it should deploy the rabbitMQ instance and install all its required dependencies. 
	
2. Backend
	In root folder of repo, run:
		pip install -r requirements.txt
	
	Then in root folder run:
		python __main__.py 
	
	If server is running, it should say 'start consuming'. 
	
3. Clients
	To start clients, in root directory run:
	python client/smart_meter_app.py
	
	You can do this in as many terminal windows to create new client windows. 
	- This should attempt to connect to RabbitMQ
