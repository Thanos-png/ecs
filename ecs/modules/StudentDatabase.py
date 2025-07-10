import json
import os
from collections import defaultdict
import bisect
from ecs.modules.Student import Student


class StudentDatabase:
    def __init__(self, db_file="student_database.json", auto_load=True):
        self.db_file = db_file
        self._by_user_id = []  # O(1) average case
        self._by_name = []  # O(1) average case
        self._user_id_dict = {}
        self._name_dict = defaultdict(list)  # Multiple students might have same name

        # Load existing data only if requested
        if auto_load:
            self.load_from_file()

    def _normalize_name(self, name):
        """Normalize name by removing accents, converting to uppercase, and trimming spaces"""
        try:
            from ecs.modules.utils import remove_greek_accents
            normalized = remove_greek_accents(name.strip())
            normalized = normalized.upper()
            normalized = " ".join(normalized.split())
            return normalized
        except Exception as e:
            print(f"ERROR: Failed to normalize name '{name}': {e}")
            return name.upper().strip()

    def add_student(self, student):
        """Add a student to all data structures"""
        try:
            # Check if student already exists (by user_id)
            if student.user_id in self._user_id_dict:
                # Update existing student
                self.remove_student_by_id(student.user_id)

            # Add to sorted lists for O(log n) search
            bisect.insort(self._by_user_id, (student.user_id, student))

            # Normalize name for consistent searching
            normalized_name = self._normalize_name(student.name)
            bisect.insort(self._by_name, (normalized_name, student))

            # Add to dictionaries for O(1) search
            self._user_id_dict[student.user_id] = student
            self._name_dict[normalized_name].append(student)

            return True

        except Exception as e:
            print(f"ERROR: Failed to add student {student.name}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def remove_student_by_id(self, user_id):
        """Remove a student by user_id from all data structures"""
        if user_id not in self._user_id_dict:
            print(f"WARNING: Student {user_id} not found in database")
            return False

        try:
            student = self._user_id_dict[user_id]
            normalized_name = self._normalize_name(student.name)

            # Remove from sorted lists
            self._by_user_id.remove((user_id, student))
            self._by_name.remove((normalized_name, student))

            # Remove from dictionaries
            del self._user_id_dict[user_id]
            self._name_dict[normalized_name].remove(student)
            if not self._name_dict[normalized_name]:  # Remove empty list
                del self._name_dict[normalized_name]

            return True
        except Exception as e:
            print(f"ERROR: Failed to remove student {user_id}: {e}")
            return False

    def find_by_user_id(self, user_id):
        """Find student by user_id in O(1) average time using dictionary"""
        # Try the exact ID first
        result = self._user_id_dict.get(user_id)
        if result:
            return result

        # If not found, try with 'p' prefix if it doesn't have one
        if not user_id.startswith('p'):
            prefixed_id = 'p' + user_id
            result = self._user_id_dict.get(prefixed_id)
            if result:
                return result

        # If not found, try without 'p' prefix if it has one
        if user_id.startswith('p'):
            clean_id = user_id[1:]
            result = self._user_id_dict.get(clean_id)
            if result:
                return result

        # Not found in any format
        return None

    def find_by_name(self, name):
        """Find students by name in O(1) average time using dictionary"""
        normalized_name = self._normalize_name(name)
        return self._name_dict.get(normalized_name, [])

    def search_partial_name(self, partial_name):
        """Search for students whose names contain the partial name"""
        normalized_partial = self._normalize_name(partial_name)
        results = []

        for normalized_name, students in self._name_dict.items():
            if normalized_partial in normalized_name:
                results.extend(students)

        return results

    def get_all_students(self):
        """Get all students sorted by user_id"""
        return [student for _, student in self._by_user_id]

    def get_all_students_by_name(self):
        """Get all students sorted by name"""
        return [student for _, student in self._by_name]

    def size(self):
        """Get total number of students"""
        return len(self._by_user_id)

    def clear(self):
        """Clear all data"""
        print(f"DEBUG: Clearing database (had {self.size()} students)")
        self._by_user_id = []
        self._by_name = []
        self._user_id_dict = {}
        self._name_dict = defaultdict(list)

    def save_to_file(self):
        """Save the database to a JSON file"""
        try:
            # Convert all students to dictionaries
            students_data = []
            for student in self.get_all_students():
                students_data.append(student.to_dict())

            # Save to file
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'students': students_data,
                    'total_count': len(students_data)
                }, f, ensure_ascii=False, indent=2)

            print(f"Database saved to {self.db_file} ({len(students_data)} students)")
            return True
        except Exception as e:
            print(f"Error saving database: {e}")
            return False

    def load_from_file(self):
        """Load the database from a JSON file"""
        if not os.path.exists(self.db_file):
            print(f"No existing database found at {self.db_file}")
            return False

        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Clear existing data only if there are data
            if self.size() > 0:
                print(f"DEBUG: Clearing existing {self.size()} students before loading")
                self.clear()

            # Load students
            students_data = data.get('students', [])
            for student_dict in students_data:
                student = Student(**student_dict)
                self.add_student(student)

            print(f"Loaded {len(students_data)} students from {self.db_file}")
            return True
        except Exception as e:
            print(f"Error loading database: {e}")
            return False

    def get_database_info(self):
        """Get information about the current database"""
        if not os.path.exists(self.db_file):
            return "No database file found"

        try:
            file_size = os.path.getsize(self.db_file)
            file_size_mb = file_size / (1024 * 1024)

            return f"""Database Info:
- File: {self.db_file}
- Students: {self.size()}
- File size: {file_size_mb:.2f} MB
- Last modified: {os.path.getmtime(self.db_file)}"""
        except Exception as e:
            return f"Error getting database info: {e}"
