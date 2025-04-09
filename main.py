import argparse
from modules.display import show_banner, show_search_header
from modules.scraper import ClassScraper
from modules.credentials import UserCredentials

def main():
    parser = argparse.ArgumentParser(description="Scrape AUEB eClass student data.")
    parser.add_argument("--scrape", action="store_true", help="Scrape user data and write to file")
    parser.add_argument("--search", metavar="AM", help="Search by student ID")
    parser.add_argument("--name", metavar="NAME", help="Search by student name if ID not provided")
    args = parser.parse_args()

    show_banner()

    if args.scrape:
        # Get credentials from the user
        credentials = UserCredentials()

        # Scrape users from the eclass.aueb.gr website
        scraper = ClassScraper(credentials)
        scraper.login()
        course_codes = scraper.get_course_codes()
        if not course_codes:
            print("No courses found. Exiting.")
            return

    # Search for a specific user
    if args.search is not None:
        show_search_header()
        print(f"Searching for student ID: {args.search}")
        # Logic to search and print data by AM

    elif args.name is not None:
        show_search_header()
        print(f"Searching for student name: {args.name}")
        # Logic to search and print data by name

    elif not args.scrape:
        show_search_header()
        am_anaz = input("Student ID: ")
        if am_anaz == "":
            name_anaz = input("Full Name: ")

if __name__ == "__main__":
    main()
