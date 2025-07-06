# eClass Scraper (ECS)
A command-line tool for scraping student data from the Athens University of Economics and Business (AUEB) eClass system.

## Features
* Login securely with your credentials
* Fetch and save student data to a file
* Search by student ID or name with O(1) performance
* Support for multiple course databases
* CLI-friendly with argument parsing

## Quick Start

### Prerequisites
* requests
* beautifulsoup4

### Installation
1. Clone the repository:
```bash
git clone https://github.com/Thanos-png/ecs.git
cd ecs
```

2. Install the scraper tool:
```bash
pip install .
```

## Credentials
Your credentials are securely requested on runtime via terminal prompts. No hardcoded values are stored.

## Usage
### Scrape Users:
```
ecs --scrape
```
This will log into the system, fetch user data, and save it to ```data/user-ids-{course code}.txt```.

### Search by Student ID:
```
ecs --search 1234567
```

### Search by Full Name:
```
ecs --name "Αθανάσιος Παναγιωτίδης"
```

## Common Errors
#### Code changes not reflected when testing
**Problem:** After modifying the source code, running `ecs` commands still uses the old version.

**Cause:** The package was installed in standard mode, which creates a cached/compiled version that doesn't update when you change the source.

**Solution:** Install in development mode for live code updates:
```bash
pip uninstall eClass-Scraper
pip install -e .
```

## Contributing
Contributions are welcome! Please feel free to fork the repository and submit a pull request.

## Contact
For questions or feedback, feel free to reach me out:
* **Email:** thanos.panagiotidis@protonmail.com
