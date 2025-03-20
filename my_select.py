from tabulate import tabulate
from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session, aliased

from models.models import Student, Grade, Teacher, Subject, Group
from conf.db import SessionLocal

# Функція для виведення таблиці
def print_table(data, headers):
    print(tabulate(data, headers=headers, tablefmt="grid"))

# 1. Знайти 5 студентів із найбільшим середнім балом з усіх предметів
def select_1(session: Session):
    query = (
        select(Student, func.avg(Grade.grade).label("avg_grade"))
        .join(Grade)
        .group_by(Student.id)
        .order_by(desc("avg_grade"))
        .limit(5)
    )
    results = session.execute(query).all()
    
    formatted_results = [(student.full_name, f"{avg_grade:.2f}") for student, avg_grade in results]
    print("1. Знайти 5 студентів із найбільшим середнім балом з усіх предметів:")
    print_table(formatted_results, ["Full Name", "Average Grade"])

# 2. Знайти студента із найвищим середнім балом з певного предмета
def select_2(session: Session, subject_id: int):
    query = (
        select(Student, Subject.name, func.avg(Grade.grade).label("avg_grade"))
        .join(Grade, Student.id == Grade.student_id) 
        .join(Subject, Subject.id == Grade.subject_id) 
        .filter(Subject.id == subject_id)
        .group_by(Student.id, Subject.name)
        .order_by(desc("avg_grade"))
        .limit(1)
    )
    result = session.execute(query).one_or_none()
    
    if result:
        student, subject_name, avg_grade = result
        
        formatted_result = [(subject_name, student.full_name, f"{avg_grade:.2f}")]
        print("2. Знайти студента із найвищим середнім балом з певного предмета:")
        print_table(formatted_result, ["Subject", "Full Name", "Average Grade"])

# 3. Знайти середній бал у групах з певного предмета
def select_3(session: Session, subject_id: int):
    query = (
        select(Group.name, Subject.name, func.avg(Grade.grade).label("avg_grade"))
        .join(Student, Student.group_id == Group.id)  
        .join(Grade, Grade.student_id == Student.id)  
        .join(Subject, Subject.id == Grade.subject_id)  
        .filter(Subject.id == subject_id)
        .group_by(Group.name, Subject.name)
        .order_by(desc("avg_grade"))
    )
    
    results = session.execute(query).all()
    
    formatted_results = [(subject_name, group_name, f"{avg_grade:.2f}") for group_name, subject_name, avg_grade in results]
    
    print("3. Знайти середній бал у групах з певного предмета:")
    print_table(formatted_results, ["Subject", "Group Name", "Average Grade"])

# 4. Знайти середній бал на потоці (по всій таблиці оцінок)
def select_4(session: Session):
    query = select(func.avg(Grade.grade).label("avg_grade"))
    result = session.execute(query).scalar()
    print(f"4. Середній бал на потоці (по всій таблиці оцінок): {result:.2f}")

# 5. Знайти які курси читає певний викладач
def select_5(session: Session, teacher_id: int):
    query = (
        select(Teacher.full_name, Subject.name)
        .join(Subject, Subject.teacher_id == Teacher.id)
        .filter(Teacher.id == teacher_id)
    )
    
    results = session.execute(query).all()
    
    formatted_results = [(teacher_name, subject_name) for teacher_name, subject_name in results]
    
    print("5. Знайти які курси читає певний викладач:")
    print_table(formatted_results, ["Teacher Name", "Subject Name"])

# 6. Знайти список студентів у певній групі
def select_6(session: Session, group_id: int):
    query = (
        select(Group.name, Student.full_name)
        .join(Group)
        .filter(Student.group_id == group_id)
        .order_by(Student.full_name.asc())
    )

    results = session.execute(query).all()

    formatted_results = [(idx + 1, group_name, student_name) for idx, (group_name, student_name) in enumerate(results)]
    
    print("6. Знайти список студентів у певній групі:")
    print_table(formatted_results, ["#", "Group Name", "Full Name"])

# 7. Знайти оцінки студентів у окремій групі з певного предмета
def select_7(session: Session, group_id: int, subject_id: int):
    query = (
        select(Student.full_name, Grade.grade, Group.name, Subject.name, Grade.date_received)  
        .join(Group, Student.group_id == Group.id)  
        .join(Grade, Grade.student_id == Student.id)  
        .join(Subject, Grade.subject_id == Subject.id)  
        .filter(Group.id == group_id, Subject.id == subject_id) 
        .order_by(Grade.date_received.desc())  
    )
    results = session.execute(query).all()

    formatted_results = [(subject_name, group_name, student_name, grade, date_received) 
                         for student_name, grade, group_name, subject_name, date_received in results]
    
    print("7. Знайти оцінки студентів у окремій групі з певного предмета, відсортовані за датою виставлення оцінки:")
    print_table(formatted_results, ["Subject Name", "Group Name", "Full Name", "Grade", "Date Received"])

# 8. Знайти середній бал, який ставить певний викладач зі своїх предметів.
def select_8(session: Session, teacher_id: int, student_id: int):
     query = (
        select(Teacher.full_name, Subject.name, func.avg(Grade.grade))
        .join(Subject, Subject.id == Grade.subject_id)
        .join(Teacher, Teacher.id == Subject.teacher_id)
        .filter(Teacher.id == teacher_id)
        .group_by(Subject.id)
     )

     results = session.execute(query).all()

     formatted_results = [(idx + 1, teacher_name, subject_name, round(avg_grade, 2) if avg_grade is not None else None) 
                         for idx, (teacher_name, subject_name, avg_grade) in enumerate(results)]

     print(f"Середній бал, який викладач ставить за предмет:")
     print_table(formatted_results, ["#", "Teacher Name", "Subject Name", "Average Grade"])

# 9. Список курсів, які відвідує певний студент
def select_9(session: Session, student_id: int):
    
    student = session.query(Student).filter(Student.id == student_id).one_or_none()
    if student:        
        query = (
            select(Subject.name)
            .distinct()  
            .join(Grade, Grade.subject_id == Subject.id)  
            .filter(Grade.student_id == student_id)  
            .order_by(Subject.name)  
        )
       
        results = session.execute(query).fetchall()
       
        formatted_results = [(index + 1, subject_name) for index, (subject_name,) in enumerate(results)]

        print(f"9. Список курсів, які відвідує студент {student.full_name}:")
        print_table(formatted_results, ["Subject Number", "Subject Name"])
    else:
        print(f"Студент з ID {student_id} не знайдений.")

# 10. Список курсів, які певному студенту читає певний викладач
def select_10(session: Session, student_id: int, teacher_id: int):    
    
    teacher = session.execute(select(Teacher.full_name).filter(Teacher.id == teacher_id)).scalar()
    student = session.execute(select(Student.full_name).filter(Student.id == student_id)).scalar()
    if not teacher:
        print(f"Викладача з ID {teacher_id} не знайдено.")
        return
    if not student:
        print(f"Студента з ID {student_id} не знайдено.")
        return
    query = (
        select(Subject.name)
        .distinct()  
        .join(Teacher, Teacher.id == Subject.teacher_id) 
        .join(Grade, Grade.subject_id == Subject.id)  
        .join(Student, Student.id == Grade.student_id)  
        .filter(Grade.student_id == student_id, Teacher.id == teacher_id)  
    )

    results = session.execute(query).all()
    

    if results:  
        formatted_results = [
            (index + 1, subject_name[0])
            for index, subject_name in enumerate(results)
        ]
        print(f"10. Список курсів, які студенту {student} читає викладач {teacher}:")
        print_table(formatted_results, ["No.", "Subject Name"])
    else:
        print(f"Немає предметів, які викладає викладач {teacher} студенту {student}.")

# 11. Середній бал, який певний викладач ставить певному студентові
def select_11(session: Session, teacher_id: int, student_id: int):
    
    student_alias = aliased(Student)
    
    result = session.query(
        Teacher.full_name.label('teacher_name'),
        student_alias.full_name.label('student_name'),
        func.avg(Grade.grade).label('avg_grade')
    ).join(Grade, Grade.student_id == student_alias.id) \
     .join(Subject, Subject.id == Grade.subject_id) \
     .join(Teacher, Teacher.id == Subject.teacher_id) \
     .filter(Teacher.id == teacher_id) \
     .filter(Grade.student_id == student_id) \
     .group_by(Teacher.id, student_alias.id) \
     .one_or_none()  

    
    if result:
        teacher_name, student_name, avg_grade = result
        avg_grade = round(avg_grade, 2) if avg_grade is not None else None
        print(f"8. Середній бал, який викладач {teacher_name} ставить студенту {student_name}: {avg_grade}")
    else:
        print("8. Оцінок не знайдено для вказаного викладача та студента.")

# 12. Оцінки студентів у певній групі з певного предмета на останньому занятті
def select_12(session: Session, group_id: int, subject_id: int):
    query = (
        select(Student.first_name, Student.last_name, Grade.grade)
        .join(Grade)
        .join(Grade.subject)
        .filter(Student.group_id == group_id, Subject.id == subject_id)
        .order_by(Grade.date_received.desc())
    ).limit(1)
    results = session.execute(query).all()
    formatted_results = [(student.first_name + ' ' + student.last_name, grade) for student, grade in results]
    print_table(formatted_results, ["Full Name", "Grade"])


if __name__ == "__main__":
    session: Session = SessionLocal()

    select_1(session)
    select_2(session, 26)
    select_3(session, 21)
    select_4(session)
    select_5(session, 8)
    select_6(session, 16)
    select_7(session, 16, 21)
    # select_8(session, 9, 121)
    select_9(session, 141)
    select_10(session, 121, 9)
    select_11(session, 9, 121)
    