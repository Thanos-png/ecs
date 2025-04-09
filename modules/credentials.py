import getpass
import os
from dotenv import load_dotenv

class UserCredentials:
    def __init__(self):
        # Load credentials from environment variables or prompt user
        load_dotenv()
        
        self.username = os.getenv('ECLASS_USERNAME')
        self.password = os.getenv('ECLASS_PASSWORD')
        
        # Prompt for credentials if not available in environment
        if not self.username:
            self.username = getpass.getpass(prompt="Username: ")
        if not self.password:
            self.password = getpass.getpass(prompt="Password: ")
            
        # Never print credentials
        print("Credentials loaded successfully")
        
        # These should be obtained dynamically rather than hardcoded
        self.execution = self._get_execution_token()
        self.eventId = "submit"
        self.json_response = self._build_json_endpoint()
    
    def _get_execution_token(self):
        """Get the execution token from the login page dynamically"""
        # This method should be implemented to fetch the token from the login page
        # For now, return the hardcoded value
        return "68732e55-d6b4-4e78-ac4c-e1bc23d746e5_..."  # Shortened for brevity
    
    def _build_json_endpoint(self, course_code="INF198"):
        """Build the JSON endpoint URL with the given course code"""
        return f"https://eclass.aueb.gr/modules/user/userslist.php?course={course_code}&sEcho=1&iColumns=2&sColumns=%2C&iDisplayStart=0&iDisplayLength=10&mDataProp_0=0&sSearch_0=&bRegex_0=false&bSearchable_0=true&bSortable_0=true&mDataProp_1=1&sSearch_1=&bRegex_1=false&bSearchable_1=true&bSortable_1=true&sSearch=&bRegex=false&iSortCol_0=0&sSortDir_0=asc&iSortingCols=1&_=1678298218568"
    
    # Getters remain the same
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
