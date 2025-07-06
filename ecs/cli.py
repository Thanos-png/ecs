import argparse
import os
import glob
from ecs.modules.display import show_banner, show_search_header
from ecs.modules.scraper import ClassScraper
from ecs.modules.credentials import UserCredentials
from ecs.modules.StudentDatabase import StudentDatabase


data_dir = "data"  # Directory where student databases are stored


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
        elif (len(user_id) == 7 or len(user_id) == 8 and user_id[0].isalpha() and user_id[1:].isdigit()):
            return user_id[1:]  # Remove the first character and return just the numbers

        # Invalid format
        else:
            print("Invalid ID format. Please enter a student ID (e.g., 1234567 or p1234567)")
            user_id = input("Student ID: ").strip()
            search_id = user_id


def select_database():
    """Let user select which course database to search"""
    db_files = glob.glob(os.path.join(data_dir, "students_*.json"))

    if not db_files:
        print(f"No student databases found in {data_dir}/ directory. Please run --scrape first.")
        return None

    if len(db_files) == 1:
        return db_files[0]

    print("\nAvailable databases:")
    for i, db_file in enumerate(db_files, 1):
        filename = os.path.basename(db_file)
        course_code = filename.replace("students_", "").replace(".json", "")
        # Get database info
        db = StudentDatabase(db_file)
        print(f"{i}. {course_code} ({db.size()} students)")

    while True:
        try:
            choice = input(f"\nSelect database (1-{len(db_files)}): ")
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(db_files):
                return db_files[choice_index]
            else:
                print(f"Invalid selection. Please enter a number between 1 and {len(db_files)}.")
        except ValueError:
            print("Please enter a valid number.")


def format_student_output(student):
    """Format student information for console output"""
    print("+" + "―" * 69 + "+")
    print(f"| Full Name: {student.name:<56} |")
    print(f"| Student-ID: {student.user_id:<55} |")
    print(f"| Position: {student.position:<57} |")

    if student.email and student.email != "N/A":
        print(f"| Email: {student.email:<60} |")

    if student.phone and student.phone != "N/A":
        print(f"| Phone: {student.phone:<60} |")

    print(f"| Department: {student.department:<55} |")
    print(f"| Registration Date: {student.date:<48} |")
    print(f"| Years: {student.years:<60} |")
    print(f"| DB-ID: {student.db_id:<60} |")
    print("+" + "―" * 69 + "+")


def main():
    parser = argparse.ArgumentParser(description="Scrape AUEB eClass student data.")
    parser.add_argument("--scrape", action="store_true", help="Scrape user data and write to file")
    parser.add_argument("--search", metavar="STUDENT_ID", help="Search by student ID")
    parser.add_argument("--name", metavar="NAME", help="Search by student name if ID not provided")
    parser.add_argument("--info", action="store_true", help="Show database information")
    args = parser.parse_args()

    show_banner()

    if args.scrape:
        # Get credentials from the user
        credentials = UserCredentials()

        # Scrape users from the eclass.aueb.gr website
        scraper = ClassScraper(credentials)
        scraper.scrape_users()

    # Search for a specific user
    elif args.search is not None:
        show_search_header()

        # Select database to search
        db_file = select_database()
        if not db_file:
            return

        # Load database
        db = StudentDatabase(db_file)

        # Validate and format the Student ID
        search_id = get_valid_student_id(args.search.strip())
        if not search_id:
            print("Invalid student ID format.")
            return

        filename = os.path.basename(db_file)
        course_code = filename.replace("students_", "").replace(".json", "")
        print(f"Searching for student ID: {search_id}")

        # Search for student
        student = db.find_by_user_id(search_id)
        if student:
            print(f"\nFound student:")
            format_student_output(student)
        else:
            print(f"No student found with ID: {search_id}")

    elif args.name is not None:
        show_search_header()

        # Select database to search
        db_file = select_database()
        if not db_file:
            return

        # Load database
        db = StudentDatabase(db_file)

        filename = os.path.basename(db_file)
        course_code = filename.replace("students_", "").replace(".json", "")

        # Remove the Greek accents from the name
        search_name = args.name.strip()
        from ecs.modules.utils import remove_greek_accents
        search_name = remove_greek_accents(search_name)

        # Format the name
        search_name = search_name.upper()

        # Remove any extra spaces
        search_name = " ".join(search_name.split())

        print(f"Searching for student name: {search_name}")

        # Search for students
        students = db.find_by_name(search_name)
        if students:
            print(f"\nFound {len(students)} student(s):")
            for student in students:
                format_student_output(student)
        else:
            # Try partial name search
            print("Exact match not found. Trying partial search...")
            partial_students = db.search_partial_name(search_name)
            if partial_students:
                print(f"\nFound {len(partial_students)} student(s) with partial match:")
                for student in partial_students:
                    format_student_output(student)
            else:
                print(f"No students found matching: {search_name}")

    elif args.info:
        # Show information about all databases
        db_files = glob.glob(os.path.join(data_dir, "students_*.json"))
        if not db_files:
            print(f"No student databases found in {data_dir}/ directory. Please run --scrape first.")
        else:
            print("Database Information:")
            print("=" * 50)
            print(f"Data directory: {os.path.abspath(data_dir)}")
            print()
            for db_file in db_files:
                filename = os.path.basename(db_file)
                course_code = filename.replace("students_", "").replace(".json", "")
                db = StudentDatabase(db_file)
                print(f"\nCourse: {course_code}")
                print(f"Students: {db.size()}")
                print(f"File: {filename}")
                file_size = os.path.getsize(db_file) / 1024  # KB
                print(f"Size: {file_size:.1f} KB")

    else:
        # No arguments provided, show help
        parser.print_help()

if __name__ == "__main__":
    main()
