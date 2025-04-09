import requests
from bs4 import BeautifulSoup
import datetime
import logging
import time
import re
from modules.utils import progress_bar

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

class ClassScraper:
    def __init__(self, user_instance):
        self.user = user_instance
        self.session = requests.Session()
        self.login_url = "https://sso.aueb.gr/login?service=https%3A%2F%2Feclass.aueb.gr%2Fmodules%2Fauth%2Fcas.php"
        self.base_url = "https://eclass.aueb.gr"
        self.courses_url = f"{self.base_url}/main/my_courses.php"
        self.course_code = "INF000"  # Default course code
        self.output_file = f"user-ids-{self.course_code}.txt"

    def login(self):
        """Authenticate with the eClass system"""
        logging.info("Logging in to eClass")

        # First, get a valid session by visiting the base URL
        try:
            self.session.get(self.base_url)
        except Exception as e:
            logging.error(f"Error accessing base URL: {e}")

        payload = {
            "username": self.user.get_username(),
            "password": self.user.get_password(),
            "execution": self.user.get_execution(),
            "_eventId": self.user.get_eventId(),
            "submit": "Login"
        }

        try:
            # Use the session from the user credentials object if available
            if hasattr(self.user, 'get_session') and callable(getattr(self.user, 'get_session')):
                self.session = self.user.get_session()

            # Post to login URL
            response = self.session.post(self.login_url, data=payload, allow_redirects=True)

            # Debug the response URL to see where I ended up
            logging.info(f"Login redirected to: {response.url}")

            # Multiple ways to check for successful login
            if ("Αποσύνδεση" in response.text or 
                "Έξοδος" in response.text or 
                "Logout" in response.text):
                logging.info("Login successful")
                return True

            # Try accessing the courses page, if we can access it, login was successful
            courses_response = self.session.get(self.courses_url)
            if courses_response.status_code == 200:
                # Save a copy of the courses page for debugging if needed
                # with open("courses_debug.html", "w", encoding="utf-8") as f:
                #     f.write(courses_response.text)

                # Look for indicators that we're logged in
                if ("Αποσύνδεση" in courses_response.text or 
                "Έξοδος" in courses_response.text or 
                "Logout" in courses_response.text or
                "Τα μαθήματά μου" in courses_response.text or 
                "My Courses" in courses_response.text):
                    logging.info("Login successful (verified via courses page)")
                    return True
                
            # If we can get course codes, we must be logged in
            soup = BeautifulSoup(courses_response.text, 'html.parser')
            course_links = soup.find_all('a', href=lambda href: href and '/courses/' in href)
            
            if course_links:
                logging.info(f"Login successful (found {len(course_links)} course links)")
                return True
                
            # If we don't see login form, we're probably logged in
            if "password" not in courses_response.text.lower() and "username" not in courses_response.text.lower():
                logging.info("Login appears successful (no login form found)")
                return True

            logging.error("Login failed. Please check your credentials.")
            return False

        except Exception as e:
            logging.error(f"Error during login: {e}")
            return False

    def get_course_codes(self):
        """Get the list of course codes and names from the user's courses page"""
        try:
            response = self.session.get(self.courses_url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching course list: {e}")
            return []

        # Ensure the request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            courses = []

            for td in soup.find_all('td'):
                strong_tag = td.find('strong')
                if strong_tag and strong_tag.find('a'):
                    link = strong_tag.find('a')
                    href = link['href']

                    if '/courses/' in href:
                        course_code = href.split('/courses/')[1].strip('/')
                        course_name = link.text.strip()
                        courses.append({
                            'code': course_code,
                            'name': course_name
                        })

            logging.info(f"Found {len(courses)} course codes")
            return courses
        else:
            logging.error(f"Failed to fetch course codes. Status code: {response.status_code}")
            return []

    def get_user_list(self, course_code):
        """Get the list of users for a specific course using the JSON endpoint"""
        # First visit the course page to establish context
        course_url = f"{self.base_url}/courses/{course_code}/"

        try:
            # Visit the course page first
            course_resp = self.session.get(course_url)
            if course_resp.status_code != 200:
                logging.warning(f"Could not access course page for {course_code}: {course_resp.status_code}")
        except Exception as e:
            logging.warning(f"Error accessing course page: {e}")

        # Try to get the user list
        json_url = f"{self.base_url}/modules/user/userslist.php?course={course_code}&sEcho=1&iColumns=2&sColumns=%2C&iDisplayStart=0&iDisplayLength=1000"

        try:
            headers = {
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Referer": course_url
            }

            response = self.session.get(json_url, headers=headers)

            # Debug information
            if response.status_code != 200:
                logging.error(f"User list request failed with status {response.status_code}")
                return []

            # Check if response is JSON
            try:
                data = response.json()
                return data.get("aaData", [])
            except ValueError:
                # If not JSON, save response for debugging
                with open("userslist_error.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                logging.error("Failed to parse JSON response from users list endpoint")

                # Attempt to find an alternative way to get user data
                logging.info("Trying alternative method to get users...")
                try:
                    # Try to get users from the participants page instead
                    participants_url = f"{self.base_url}/modules/user/users.php?course={course_code}"
                    part_resp = self.session.get(participants_url)

                    if part_resp.status_code == 200:
                        soup = BeautifulSoup(part_resp.text, 'html.parser')
                        users = []

                        user_rows = soup.select("table.table-default tr")
                        for row in user_rows[1:]:  # Skip header row
                            try:
                                cells = row.find_all('td')
                                if len(cells) >= 2:
                                    # First cell contains name
                                    user_link = cells[0].find('a')

                                    # Second cell contains position
                                    position = cells[1].text.strip() if len(cells) > 1 else "N/A"

                                    if user_link:
                                        user_name = user_link.text.strip()
                                        href = user_link.get('href', '')
                                        # Extract DB ID from href
                                        db_id = href.split('uid=')[-1] if 'uid=' in href else 'unknown'

                                        users.append({
                                            "0": f"<a href='{href}'>{user_name}</a>",
                                            "1": position,
                                            "DT_RowId": db_id
                                        })
                            except Exception as e:
                                logging.warning(f"Error parsing user row: {e}")

                        logging.info(f"Found {len(users)} users using alternative method")
                        return users
                except Exception as e:
                    logging.error(f"Alternative method failed too: {e}")

                return []
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching user list for course {course_code}: {e}")
            return []

    def scrape_users(self):
        """Main method to scrape user information"""
        if not self.login():
            return False

        courses = self.get_course_codes()
        if not courses:
            logging.error("No courses found")
            return False

        # Display course menu
        print("\nAvailable courses:")
        for i, course in enumerate(courses, 1):
            print(f"{i}. [{course['code']}] {course['name']}")

        # Get user selection
        while True:
            try:
                choice = input("\nSelect a course number (or 'q' to quit): ")

                if choice.lower() == 'q':
                    logging.info("User chose to quit.")
                    return False

                choice_index = int(choice) - 1
                if 0 <= choice_index < len(courses):
                    selected_course = courses[choice_index]
                    self.course_code = selected_course['code']
                    break
                else:
                    print(f"Invalid selection. Please enter a number between 1 and {len(courses)}.")
            except ValueError:
                print("Please enter a valid number or 'q' to quit.")

        logging.info(f"Selected course: {self.course_code} ({courses[choice_index]['name']})")

        # Update output file name with selected course code
        self.output_file = f"user-ids-{self.course_code}.txt"

        # Get users for selected course
        user_list = self.get_user_list(self.course_code)
        logging.info(f"Retrieved {len(user_list)} users")

        if not user_list:
            logging.warning("No users found for this course.")
            return False

        with open(self.output_file, "w", encoding="utf-8") as f:
            total = len(user_list) if user_list else 1
            progress_bar(0, total)

            for i, user in enumerate(user_list):
                try:
                    # Parse user data
                    user_data = self.parse_user(user)

                    # Write to file
                    f.write("+" + "―" * 69 + "+\n")
                    f.write(self.format_user_info(user_data))

                    # Update progress bar
                    progress_bar(i + 1, total)

                    # Add a small delay to avoid overloading the server
                    time.sleep(0.2)
                except Exception as e:
                    logging.warning(f"Error processing user {i+1}: {e}")
                    # Update progress bar even on error
                    progress_bar(i + 1, total)
                    continue

            f.write("+" + "―" * 69 + "+\n")
            print()  # Add a newline after progress bar completes
            logging.info(f"User data written to {self.output_file}")

        return True

    def parse_user(self, user):
        """Extract user information from user data"""
        try:
            name = user["0"].split(">")[-2][:-3]
            position = user["1"][7:-8]
            db_id = user["DT_RowId"]

            # Extract link more safely
            link_parts = user["0"].split("href='/")
            if len(link_parts) > 1:
                link_part = link_parts[1].split("'>")[0]
                link_part = link_part.split("&amp;")
                link_part = link_part[0] + "&" + link_part[1]
                # Remove the potentially problematic substring manipulation
                link = f"{self.base_url}/{link_part}"
            else:
                raise ValueError("Could not extract user profile link")

            # Fetch user profile page
            response = self.session.get(link)
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract User ID (student ID)
            user_id_div = soup.find("div", class_="not_visible")
            user_id = user_id_div.text if user_id_div else "N/A"

            # Extract profile data
            profile_div = soup.find("div", class_="profile-content-panel-text")
            if not profile_div:
                raise ValueError("Profile data not found")

            # Initialize values
            phone = ""
            email = ""
            department = "N/A"
            date = "N/A"
            years = "N/A"

            # Each piece of information is in its own div with a span for the label
            for div in profile_div.find_all("div", style="line-height:26px;"):
                span = div.find("span")
                if not span:
                    continue

                label = span.text.strip()
                # Get the text content after the span (the value)
                value = div.get_text().replace(span.get_text(), "", 1).strip()

                if "Τηλέφωνο:" in label:  # Phone
                    phone = value

                elif "E-mail:" in label:  # Email
                    # Handle the email that might be in a script
                    email_link = div.find("a")
                    if email_link:
                        email = email_link.text.strip()
                    else:
                        email = value if value and value != "(e-mail address hidden)" else ""

                elif "Κατηγορία:" in label:  # Department
                    department = value

                elif "Μέλος από:" in label:  # Registration date
                    date = value
                    # Extract just the year (4 digits)
                    year_match = re.search(r'(\d{4})', value)
                    if year_match:
                        years = year_match.group(1)

            # Calculate year
            current_year = datetime.date.today().year
            current_month = datetime.date.today().month
            try:
                years = current_year - int(years) + (1 if current_month >= 9 else 0)
            except (ValueError, TypeError):
                years = "N/A"

            return {
                "name": name,
                "user_id": user_id,
                "position": position,
                "email": email,
                "phone": phone,
                "department": department,
                "date": date,
                "years": years,
                "db_id": db_id
            }
        except Exception as e:
            logging.warning(f"Error parsing user: {e}")
            raise

    def format_user_info(self, user_data):
        """Format user information for output file"""
        lines = [
            f"| Full Name: {user_data.get('name', 'N/A')}",
            f"| Student-ID: {user_data.get('user_id', 'N/A')}",
            f"| Position: {user_data.get('position', 'N/A')}"
        ]

        # Add email if available
        if user_data.get('email'):
            lines.append(f"| Email: {user_data.get('email')}")

        # Add phone number if available
        if user_data.get('phone'):
            lines.append(f"| Phone Number: {user_data.get('phone')}")

        lines.extend([
            f"| Department: {user_data.get('department', 'N/A')}",
            f"| Registration Date: {user_data.get('date', 'N/A')}",
            f"| Years: {user_data.get('years', 'N/A')}",
            f"| DB-ID: {user_data.get('db_id', 'N/A')}"
        ])

        formatted = ""
        for line in lines:
            spaces = abs(len(line) - 70)
            formatted += line + " " * spaces + "|\n"
        return formatted
