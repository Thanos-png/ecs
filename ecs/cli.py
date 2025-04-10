import argparse
from ecs.modules.display import show_banner, show_search_header
from ecs.modules.scraper import ClassScraper
from ecs.modules.credentials import UserCredentials

def get_valid_student_id(search_id=None):
    """Get and validate a student ID"""
    while True:
        if search_id:
            user_id = search_id
        else:
            user_id = input("Student ID: ").strip()

        if not user_id:
            return None  # Empty input, will prompt for name instead

        # Check if it's only a number (e.g., 1234567)
        if ((len(user_id) == 7 or len(user_id) == 8) and user_id.isdigit()):
            return user_id  # Return the numeric ID as is

        # Check if it starts with a letter followed by digits (e.g., p1234567)
        elif (len(user_id) == 7 or len(user_id) == 8 and 
              user_id[0].isalpha() and 
              user_id[1:].isdigit()):
            return user_id[1:]  # Remove the first character and return just the numbers

        # Invalid format
        else:
            print("Invalid ID format. Please enter a student ID (e.g., 1234567 or p1234567)")
            user_id = input("Student ID: ").strip()
            search_id = user_id

def main():
    parser = argparse.ArgumentParser(description="Scrape AUEB eClass student data.")
    parser.add_argument("--scrape", action="store_true", help="Scrape user data and write to file")
    parser.add_argument("--search", metavar="STUDENT_ID", help="Search by student ID")
    parser.add_argument("--name", metavar="NAME", help="Search by student name if ID not provided")
    args = parser.parse_args()

    show_banner()

    if args.scrape:
        # Get credentials from the user
        credentials = UserCredentials()

        # Scrape users from the eclass.aueb.gr website
        scraper = ClassScraper(credentials)
        scraper.scrape_users()

    # Search for a specific user
    if args.search is not None:
        show_search_header()

        # Validate and format the Student ID if needed
        search_id = get_valid_student_id(args.search.strip())

        print(f"Searching for student ID: {search_id}")
        # Logic to search data by Student ID

    elif args.name is not None:
        show_search_header()

        # Remove the Greek accents from the name
        search_name = args.name.strip()

        # Format the name
        search_name = search_name.upper()

        # Remove any extra spaces
        search_name = " ".join(search_name.split())

        print(f"Searching for student name: {search_name}")
        # Logic to search data by Name

    elif not args.scrape:
        show_search_header()

        # Validate and format the Student ID if needed
        search_id = get_valid_student_id()

        if search_id is None:
            # Remove the Greek accents from the name
            search_name = input("Full Name: ").strip()

            # Format the name
            search_name = search_name.upper()

            # Remove any extra spaces
            search_name = " ".join(search_name.split())

            print(f"Searching for student name: {search_name}")
            # Logic to search data by Name
        else:
            print(f"Searching for student ID: {search_id}")
            # Logic to search data by Student ID

if __name__ == "__main__":
    main()
