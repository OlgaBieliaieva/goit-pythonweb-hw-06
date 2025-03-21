from tabulate import tabulate
from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session, aliased

from models.models import Student, Grade, Teacher, Subject, Group
from conf.db import SessionLocal
from utils.print_table import print_table

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
    
    formatted_results = [(idx + 1, student.full_name, f"{avg_grade:.2f}") for idx, (student, avg_grade) in enumerate(results)]
    print("1. 5 студентів із найбільшим середнім балом з усіх предметів:")
    print_table(formatted_results, ["#", "Full Name", "Average Grade"])

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
    if not result:
        print("Немає даних для вказаного предмета.")
        return    
    
    student, subject_name, avg_grade = result        
        
    print(f"2. Cтудент {student.full_name} має найвищий середній бал з предмета {subject_name}: {avg_grade: .2f} балів")

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
    if not results:
        print("Немає даних для вказаного предмета.")
        return
    
    formatted_results = [(group_name, f"{avg_grade:.2f}") for group_name, _, avg_grade in results]
    
    print(f"3. Середній бал у групах з предмета {results[0][1]}:")
    print_table(formatted_results, ["Group Name", "Average Grade"])

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

    if not results:
        print("Немає даних для вказаного вчителя.")
        return
    
    formatted_results = [(idx + 1, subject_name) for idx, (_, subject_name) in enumerate(results)]
    
    print(f"5. Викладач {results[0][0]} читає наступні курси:")
    print_table(formatted_results, ["#", "Subject Name"])

# 6. Знайти список студентів у певній групі
def select_6(session: Session, group_id: int):
    query = (
        select(Group.name, Student.full_name)
        .join(Group)
        .filter(Student.group_id == group_id)
        .order_by(Student.full_name.asc())
    )

    results = session.execute(query).all()

    if not results:
        print("Немає даних для вказаної групи.")
        return

    formatted_results = [(idx + 1, student_name) for idx, (_, student_name) in enumerate(results)]
    
    print(f"6. Список студентів у групі {results[0][0]}:")
    print_table(formatted_results, ["#", "Full Name"])

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

    if not results:
        print("Немає даних для вказаних параметрів запиту.")
        return
    
    formatted_results = [(idx + 1, student_name, grade, date_received.strftime("%d.%m.%Y")) 
                         for idx, (student_name, grade, _, _, date_received) in enumerate(results)]
    
    print(f"7. Оцінки студентів у групі {results[0][2]} з предмета {results[0][3]}, відсортовані за датою виставлення оцінки:")
    print_table(formatted_results, ["#", "Full Name", "Grade", "Date Received"])

# 8. Знайти середній бал, який ставить певний викладач зі своїх предметів.
def select_8(session: Session, teacher_id: int):
    query = (
        select(
            Teacher.full_name,
            func.avg(Grade.grade).label("avg_grade")
        )
        .join(Subject, Subject.teacher_id == Teacher.id)
        .join(Grade, Grade.subject_id == Subject.id)
        .filter(Teacher.id == teacher_id)
        .group_by(Teacher.full_name)
    )

    result = session.execute(query).first()

    if not result:
        print("Цей викладач ще не ставив оцінок.")
        return

    full_name, avg_grade = result
    print(f"8. Середній бал, який ставить викладач {full_name}: {avg_grade:.2f}")

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
        print_table(formatted_results, ["#", "Subject Name"])
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
        print_table(formatted_results, ["#", "Subject Name"])
    else:
        print(f"Немає предметів, які викладає викладач {teacher} студенту {student}.")

# 11. Середній бал, який певний викладач ставить певному студентові
def select_11(session: Session, teacher_id: int, student_id: int):

    query = (
        select(
            Teacher.first_name, Teacher.last_name,
            Student.first_name, Student.last_name,
            func.avg(Grade.grade).label("avg_grade")
        )
        .join(Subject, Subject.teacher_id == Teacher.id)
        .join(Grade, Grade.subject_id == Subject.id)
        .join(Student, Student.id == Grade.student_id)
        .filter(Teacher.id == teacher_id, Student.id == student_id)
        .group_by(Teacher.id, Student.id)
    )

    results = session.execute(query).all()

    if not results:
        print("Немає оцінок від цього викладача для цього студента.")
        return

    teacher_first, teacher_last, student_first, student_last, avg_grade = results[0]

    print(f"11. Середній бал, який {teacher_first} {teacher_last} поставив студенту {student_first} {student_last}: {avg_grade:.2f}")

# 12. Оцінки студентів у певній групі з певного предмета на останньому занятті
def select_12(session: Session, group_id: int, subject_id: int):
    last_lesson_date_query = (
        select(func.max(Grade.date_received))
        .join(Student, Student.id == Grade.student_id)
        .filter(Student.group_id == group_id, Grade.subject_id == subject_id)
    )

    last_lesson_date = session.execute(last_lesson_date_query).scalar()

    if not last_lesson_date:
        print("Немає оцінок для цієї групи з цього предмета.")
        return

    query = (
        select(
            Group.name, Subject.name, Student.first_name, Student.last_name, Grade.grade
        )
        .join(Student, Student.group_id == Group.id)
        .join(Grade, Grade.student_id == Student.id)
        .join(Subject, Subject.id == Grade.subject_id)
        .filter(Group.id == group_id, Subject.id == subject_id, Grade.date_received == last_lesson_date)
        .order_by(desc(Grade.date_received))
    )

    results = session.execute(query).all()

    if not results:
        print("Немає оцінок для цієї групи з цього предмета.")
        return

    group_name, subject_name = results[0][:2]  
    formatted_date = last_lesson_date.strftime("%d.%m.%Y")
    formatted_results = [
        (idx + 1, f"{first_name} {last_name}", grade)
        for idx, (_, _, first_name, last_name, grade) in enumerate(results)
    ]

    print(f"12. Оцінки студентів групи {group_name} з предмета {subject_name} на останньому занятті ({formatted_date}):")
    print_table(formatted_results, ["#", "Student Name", "Grade"])


if __name__ == "__main__":
    session: Session = SessionLocal()

    select_1(session)
    select_2(session, 26)
    select_3(session, 21)
    select_4(session)
    select_5(session, 8)
    select_6(session, 16)
    select_7(session, 16, 21)
    select_8(session, 10)
    select_9(session, 141)
    select_10(session, 121, 9)
    select_11(session, 9, 121)
    select_12(session, 18, 29)
    