from my_select import *
from conf.db import SessionLocal

# Список звітів
REPORTS = {
    1: ("5 студентів із найбільшим середнім балом", select_1, []),
    2: ("Студент із найвищим середнім балом з предмета", select_2, ["subject_id"]),
    3: ("Середній бал у групах з предмета", select_3, ["subject_id"]),
    4: ("Середній бал на потоці", select_4, []),
    5: ("Курси викладача", select_5, ["teacher_id"]),
    6: ("Список студентів у групі", select_6, ["group_id"]),
    7: ("Оцінки студентів у групі з предмета", select_7, ["group_id", "subject_id"]),
    8: ("Середній бал викладача", select_8, ["teacher_id"]),
    9: ("Курси, які відвідує студент", select_9, ["student_id"]),
    10: ("Курси, які студенту читає викладач", select_10, ["student_id", "teacher_id"]),
    11: ("Середній бал студента у викладача", select_11, ["teacher_id", "student_id"]),
    12: ("Оцінки студентів групи на останньому занятті з предмету", select_12, ["group_id", "subject_id"]),
}

def show_reports():
    """Виводить список доступних звітів"""
    print("\nДоступні звіти:")
    for num, (desc, _, params) in REPORTS.items():
        param_list = ", ".join(params) if params else "Без параметрів"
        print(f"{num}. {desc} ({param_list})")

def main():
    session = SessionLocal()
    while True:
        show_reports()
        try:
            report_num = int(input("\nОберіть номер звіту (або 0 для виходу): "))
            if report_num == 0:
                print("Вихід...")
                break
            if report_num not in REPORTS:
                print("Невірний номер звіту. Спробуйте ще раз.")
                continue

            desc, func, params = REPORTS[report_num]
            param_values = []
            
            for param in params:
                value = input(f"Введіть {param}: ")
                param_values.append(int(value))  
            
            print(f"\nВиконується звіт: {desc}\n")
            func(session, *param_values)  
            
        except ValueError:
            print("Помилка введення! Введіть коректний номер.")

    session.close()

if __name__ == "__main__":
    main()