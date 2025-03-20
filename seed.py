import random
from datetime import datetime, timedelta

from faker import Faker
from sqlalchemy.orm import Session

from conf.db import SessionLocal
from models.models import Student, Grade, Subject, Teacher, Group

fake = Faker("uk_UA")
Faker.seed(42)

def seed_database():
    # Create a session
    session: Session = SessionLocal()
    try:
        
        groups = create_group(session)
       
        teachers = create_teacher(session)
        
        subjects = create_subject(session, teachers)
        
        students = create_student(session, groups)
        
        create_grades(session, students, subjects)
        
        session.commit()

        print("Database seeded successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        # Close the session
        session.close()

def create_group(session: Session):
    group_name = ['CS-101', 'AI-202', 'SE-303', 'DS-404', 'IS-105', 'ML-206', 'ITM-307', 'CSN-408', 'GD-109', 'HCI-210']
    groups = []
    for name in group_name:
        group = Group(name=name)
        session.add(group)
        groups.append(group)
    session.flush()
    return groups

def create_teacher(session: Session):
    teachers = []
    for i in range(5):
        teacher = Teacher(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            phone=fake.phone_number(),
        )
        session.add(teacher)
        teachers.append(teacher)
    session.flush()
    return teachers

def create_subject(session: Session, teachers: list):
    subject_names = [
        "Алгоритми та структури даних", 
        "Об'єктно-орієнтоване програмування", 
        "Бази даних та SQL", 
        "Операційні системи", 
        "Комп'ютерні мережі", 
        "Штучний інтелект та машинне навчання", 
        "Розробка веб-застосунків", 
        "Кібербезпека", 
        "Хмарні технології", 
        "Аналіз даних та Big Data", 
        "Програмування на Python", 
        "Архітектура комп’ютерних систем", 
        "Тестування програмного забезпечення", 
        "Мобільна розробка", 
        "Розробка ігор та 3D-графіка"
    ]
    subjects = []
    for name in subject_names:
        subject = Subject(name=name, teacher=random.choice(teachers))
        session.add(subject)
        subjects.append(subject)
    session.flush()
    return subjects

def create_student(session: Session, groups: list):
    students = []
    for i in range(100):
        student = Student(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            phone=fake.phone_number(),
            group=random.choice(groups)
        )
        session.add(student)
        students.append(student)
    session.flush()
    return students

def create_grades(session: Session, students: list, subjects: list):
    start_date = datetime.now() - timedelta(days=180)
    end_date = datetime.now()

    for student in students:
        num_grades = random.randint(10, 20)
        for _ in range(num_grades):
            subject = random.choice(subjects)
            grade = Grade(
                student_id=student.id,
                subject_id=subject.id,
                grade=random.randint(40, 100),
                date_received=fake.date_between_dates(date_start=start_date, date_end=end_date)                
            )
            session.add(grade)
    session.flush()

if __name__ == "__main__":
    seed_database()