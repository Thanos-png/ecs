# eClass Scraper (ECS)
A command-line tool for scraping student data from the Athens University of Economics and Business (AUEB) eClass system.

## Features
* Login securely with your credentials
* Fetch and save student data to a file
* Optional search by student ID or name (coming soon)
* CLI-friendly with argument parsing

## Requirements
* requests
* beautifulsoup4

## Installation
1. Clone the repository:

```
git clone https://github.com/Thanos-png/ecs.git
cd ecs
```

2. Install the CLI tool:

```
pip install .
```

## Credentials
Your credentials are securely requested on runtime via terminal prompts. No hardcoded values are stored.

## Usage
### Scrape Users:
```
ecs --scrape
```
This will log into the system, fetch user data, and save it to ```user-ids.txt```.

### Search by Student ID:
```
ecs --search 123456
```

### Search by Full Name:
```
ecs --name "Thanos Panagiotidis"
```

## Contributing
Contributions are welcome! Please feel free to fork the repository and submit a pull request.

## Contact
For questions or feedback, feel free to reach me out:
* **Email:** thanos.panagiotidis@protonmail.com
