import getpass
import os
import re
import requests
from dotenv import load_dotenv


class UserCredentials:
    def __init__(self):
        # Load credentials from environment variables or prompt user
        load_dotenv()

        self.username = os.getenv('ECLASS_USERNAME')
        self.password = os.getenv('ECLASS_PASSWORD')

        # Prompt for credentials if not set
        if not self.username:
            # self.username = getpass.getpass(prompt="Username: ")
            self.username = input("Username: ")
        if not self.password:
            self.password = getpass.getpass(prompt="Password: ")

        # Debugging: print credentials
        # print(self.username)
        # print(self.password)

        # Never print credentials
        print("\nCredentials loaded successfully")

        # Get execution token dynamically
        self.execution = self._get_execution_token()
        self.eventId = "submit"
        self.json_response = self._build_json_endpoint()

        # Store session for reuse
        self.session = requests.Session()

    def _get_execution_token(self):
        """Get the execution token from the login page dynamically"""
        url = "https://eclass.aueb.gr/modules/auth/cas.php"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Extract execution token using regex
                execution_match = re.search(r'name="execution" value="([^"]+)"', response.text)
                if execution_match:
                    return execution_match.group(1)
                else:
                    print("Warning: Could not find execution token in login page")
            else:
                print(f"Warning: Failed to access login page (status {response.status_code})")
        except Exception as e:
            print(f"Error fetching execution token: {e}")

    def _build_json_endpoint(self, course_code="INF001"):
        """Build the JSON endpoint URL with the given course code"""
        return f"https://eclass.aueb.gr/modules/user/userslist.php?course={course_code}&sEcho=1&iColumns=2&sColumns=%2C&iDisplayStart=0&iDisplayLength=10&mDataProp_0=0&sSearch_0=&bRegex_0=false&bSearchable_0=true&bSortable_0=true&mDataProp_1=1&sSearch_1=&bRegex_1=false&bSearchable_1=true&bSortable_1=true&sSearch=&bRegex=false&iSortCol_0=0&sSortDir_0=asc&iSortingCols=1&_=1678298218568"

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_execution(self):
        return self.execution

    def get_eventId(self):
        return self.eventId

    def get_json_response(self):
        return self.json_response
    
    def get_session(self):
        """Return the session object for reuse"""
        return self.session
