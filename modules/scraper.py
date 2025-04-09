import requests
from bs4 import BeautifulSoup
import datetime
import logging
import time
from modules.utils import progress_bar

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

class ClassScraper:
    def __init__(self, user_instance):
        self.user = user_instance
        self.session = requests.Session()
        self.login_url = "https://sso.aueb.gr/login?service=https%3A%2F%2Feclass.aueb.gr%2Fmodules%2Fauth%2Fcas.php"
        self.base_url = "https://eclass.aueb.gr"
        self.courses_url = f"{self.base_url}/main/my_courses.php"
        self.output_file = "user-ids.txt"
        
    def login(self):
        """Authenticate with the eClass system"""
        logging.info("Logging in to eClass")
        payload = {
            "username": self.user.get_username(),
            "password": self.user.get_password(),
            "execution": self.user.get_execution(),
            "_eventId": self.user.get_eventId()
        }
        
        response = self.session.post(self.login_url, data=payload)
        
        if "Αποσύνδεση" not in response.text:  # Check for Greek text for "Logout"
            logging.error("Login failed. Please check your credentials.")
            return False
        
        logging.info("Login successful")
        return True
        
    def get_course_codes(self):
        """Get the list of course codes from the user's courses page"""
        try:
            response = self.session.get(self.courses_url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching course list: {e}")
            return []
        
        # Ensure the request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            course_codes = []

            for td in soup.find_all('td'):
                strong_tag = td.find('strong')
                if strong_tag and strong_tag.find('a'):
                    href = strong_tag.find('a')['href']
                    if '/courses/' in href:
                        course_code = href.split('/courses/')[1].strip('/')
                        course_codes.append(course_code)

            logging.info(f"Found {len(course_codes)} course codes")
            return course_codes
        else:
            logging.error(f"Failed to fetch course codes. Status code: {response.status_code}")
            return []
        
    def get_user_list(self, course_code):
        """Get the list of users for a specific course using the JSON endpoint"""
        json_url = f"{self.base_url}/modules/user/userslist.php?course={course_code}&sEcho=1&iColumns=2&sColumns=%2C&iDisplayStart=0&iDisplayLength=1000"
        
        try:
            response = self.session.get(json_url)
            response.raise_for_status()
            return response.json().get("aaData", [])
        except (requests.exceptions.RequestException, ValueError) as e:
            logging.error(f"Error fetching user list for course {course_code}: {e}")
            return []
    
    def scrape_users(self):
        """Main method to scrape user information"""
        if not self.login():
            return False
            
        course_codes = self.get_course_codes()
        if not course_codes:
            logging.error("No courses found")
            return False
            
        # Use the first course for now
        course_code = course_codes[0]
        logging.info(f"Using course: {course_code}")
        
        user_list = self.get_user_list(course_code)
        logging.info(f"Retrieved {len(user_list)} users")
        
        with open(self.output_file, "w", encoding="utf-8") as f:
            progress_bar(0, len(user_list))
            
            for i, user in enumerate(user_list):
                progress_bar(i + 1, len(user_list))
                
                try:
                    # Parse user data
                    user_data = self.parse_user(user)
                    
                    # Write to file
                    f.write("+" + "―" * 85 + "+\n")
                    f.write(self.format_user_info(user_data))
                    
                    # Add a small delay to avoid overloading the server
                    time.sleep(0.2)
                except Exception as e:
                    logging.warning(f"Error processing user {i+1}: {e}")
                    continue
                    
            f.write("+" + "―" * 85 + "+\n")
            logging.info(f"User data written to {self.output_file}")
        
        return True
        
    def parse_user(self, user):
        """Extract user information from user data"""
        try:
            name = user["0"].split(">")[-2][:-3]
            user_id = user["DT_RowId"]
            
            # Extract link more safely
            link_parts = user["0"].split("href='/")
            if len(link_parts) > 1:
                link_part = link_parts[1].split("'>")[0]
                # Remove the potentially problematic substring manipulation
                link = f"{self.base_url}/{link_part}"
            else:
                raise ValueError("Could not extract user profile link")
                
            # Fetch user profile page
            response = self.session.get(link)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract AM (student ID)
            am_div = soup.find("div", class_="not_visible")
            am = am_div.text if am_div else "N/A"
            
            # Extract profile data
            profile_div = soup.find("div", class_="profile-content-panel-text")
            if not profile_div:
                raise ValueError("Profile data not found")
                
            infoList = profile_div.text.replace(" ", "").replace("\n", "").split(":")
            phone, position, department, year = self.parse_profile(infoList)
            
            # Calculate year
            current_year = datetime.date.today().year
            current_month = datetime.date.today().month
            try:
                year = current_year - int(year) + (1 if current_month >= 9 else 0)
            except (ValueError, TypeError):
                year = "N/A"
                
            return {
                "name": name,
                "am": am,
                "user_id": user_id,
                "position": position,
                "department": department,
                "year": year,
                "phone": phone
            }
        except Exception as e:
            logging.warning(f"Error parsing user: {e}")
            raise
            
    def parse_profile(self, infoList):
        """Parse profile information with better error handling"""
        phone = ""
        position = "N/A"
        department = "N/A"
        year = "N/A"
        
        try:
            if len(infoList) == 6:
                position = infoList[1][:-9]
                department = infoList[2][:-8]
                year = infoList[3][6:10]
            elif len(infoList) == 7:
                position = infoList[2][:-9]
                department = infoList[3][:-8]
                year = infoList[4][6:10]
            elif len(infoList) == 8:
                phone = infoList[2][:-8]
                position = infoList[3][:-9]
                department = infoList[4][:-8]
                year = infoList[5][6:10]
            elif len(infoList) == 9:
                phone = infoList[2][:-8]
                position = infoList[3][:-14]
                department = infoList[5][:-8]
                year = infoList[6][6:10]
            else:
                phone = "<More Info>"
                logging.warning(f"Unexpected profile format with {len(infoList)} elements")
        except IndexError:
            logging.warning("Index error when parsing profile data")
            
        return phone, position, department, year
        
    def format_user_info(self, user_data):
        """Format user information for output file"""
        lines = [
            f"| Full Name: {user_data.get('name', 'N/A')}",
            f"| Student ID: {user_data.get('am', 'N/A')}",
        ]
        
        if user_data.get('til'):
            lines.append(f"| Phonenumber: {user_data.get('phone')}")
            
        lines.extend([
            f"| Position: {user_data.get('position', 'N/A')}",
            f"| Department: {user_data.get('department', 'N/A')}",
            f"| Year: {user_data.get('year', 'N/A')}",
            f"| DB ID: {user_data.get('user_id', 'N/A')}"
        ])
        
        formatted = ""
        for line in lines:
            spaces = abs(len(line) - 60)
            formatted += line + " " * spaces + "|\n"
        return formatted
