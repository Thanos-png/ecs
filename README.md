# eClass Scraper CLI
A command-line tool for scraping student data from the Athens University of Economics and Business (AUEB) eClass system.

## Features
* Login securely with your credentials
* Fetch and save student data to a file
* Optional search by student ID or name
* CLI-friendly with argument parsing

## Requirements
* requests
* beautifulsoup4

## Installation
1. Clone the repository:

```
git clone https://github.com/yourusername/ECS.git
cd ECS
```

2. Install dependencies:

```
pip install -r requirements.txt
```

## Credentials
Your credentials are securely requested on runtime via terminal prompts. No hardcoded values are stored.

## Usage
### Scrape Users:
```
python main.py --scrape
```
This will log into the system, fetch user data, and save it to ```user-ids.txt```.

### Search by Student ID:
```
python main.py --search 123456
```

### Search by Full Name:
```
python main.py --name "Thanos Panagiotidis"
```

## Contributing
Contributions are welcome! Please feel free to fork the repository and submit a pull request.

## Contact
For questions or feedback, feel free to reach me out:
* **Email:** thanos.panagiotidis@protonmail.com
