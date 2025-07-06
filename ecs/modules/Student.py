
class Student:
    def __init__(self, name, user_id, position, email="", phone="", department="N/A", 
                 date="N/A", years="N/A", db_id=""):
        self.name = name
        self.user_id = user_id
        self.position = position
        self.email = email
        self.phone = phone
        self.department = department
        self.date = date
        self.years = years
        self.db_id = db_id

    def __str__(self):
        return f"Student(name='{self.name}', user_id='{self.user_id}', position='{self.position}, email='{self.email}', phone='{self.phone}', department='{self.department}', date='{self.date}', years='{self.years}', db_id='{self.db_id}')"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        """Convert student to dictionary for compatibility with existing code"""
        return {
            "name": self.name,
            "user_id": self.user_id,
            "position": self.position,
            "email": self.email,
            "phone": self.phone,
            "department": self.department,
            "date": self.date,
            "years": self.years,
            "db_id": self.db_id
        }
