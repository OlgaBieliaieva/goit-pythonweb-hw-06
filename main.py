import argparse

from conf.db import SessionLocal
from models.models import Student, Group, Teacher, Subject, Grade
from utils.print_table import print_table
from reports import main as reports_main




def create_record(model_name, **kwargs):    
    session = SessionLocal()
    try:
        model_class = get_model_class(model_name)
        new_record = model_class(**kwargs)
        session.add(new_record)
        session.commit()
        print(f"{model_name} успішно створено з ID: {new_record.id}")
    except Exception as e:
        session.rollback()
        print(f"Помилка під час створення {model_name}: {e}")
    finally:
        session.close()

def list_records(model_name):    
    session = SessionLocal()
    try:
        model_class = get_model_class(model_name)
        records = session.query(model_class).all()
        if not records:
            print(f"Немає жодного запису для моделі {model_name}")
            return
        
        print(f"Список всіх {model_name}:")        
        
        headers, table_data = get_table_data(model_name, records)
        print_table(table_data, headers)
        
    except Exception as e:
        print(f"Помилка під час отримання списку {model_name}: {e}")
    finally:
        session.close()

def update_record(model_name, id, **kwargs):    
    session = SessionLocal()
    try:
        model_class = get_model_class(model_name)
        record = session.query(model_class).filter(model_class.id == id).first()
        if not record:
            print(f"{model_name} з ID {id} не знайдено")
            return
                
        old_values = {}
        for key in kwargs.keys():
            if hasattr(record, key):
                old_values[key] = getattr(record, key)
               
        for key, value in kwargs.items():
            if hasattr(record, key):
                setattr(record, key, value)
        
        session.commit()
                
        print(f"{model_name} з ID {id} успішно оновлено")
        print("Змінені поля:")
        for key, old_value in old_values.items():
            new_value = getattr(record, key)
            print(f"  {key}: {old_value} -> {new_value}")
            
    except Exception as e:
        session.rollback()
        print(f"Помилка під час оновлення {model_name}: {e}")
    finally:
        session.close()

def remove_record(model_name, id):    
    session = SessionLocal()
    try:
        model_class = get_model_class(model_name)
        record = session.query(model_class).filter(model_class.id == id).first()
        if not record:
            print(f"{model_name} з ID {id} не знайдено")
            return
                
        print(f"Видалення {model_name} з ID {id}:")
        headers, table_data = get_table_data(model_name, [record])
        print_table(table_data, headers)
        
        session.delete(record)
        session.commit()
        print(f"{model_name} успішно видалено")
    except Exception as e:
        session.rollback()
        print(f"Помилка під час видалення {model_name}: {e}")
    finally:
        session.close()

def get_model_class(model_name):    
    models = {
        'Student': Student,
        'Group': Group,
        'Teacher': Teacher,
        'Subject': Subject,
        'Grade': Grade
    }
    
    if model_name not in models:
        raise ValueError(f"Невідома модель: {model_name}. Доступні моделі: {', '.join(models.keys())}")
    
    return models[model_name]

def get_table_data(model_name, records):   
    if model_name == 'Student':
        headers = ["ID", "Повне ім'я", "Email", "Телефон", "Група"]
        data = [[r.id, r.full_name, r.email, r.phone or '', r.group_id] for r in records]
    elif model_name == 'Group':
        headers = ["ID", "Назва"]
        data = [[r.id, r.name] for r in records]
    elif model_name == 'Teacher':
        headers = ["ID", "Повне ім'я", "Email", "Телефон"]
        data = [[r.id, r.full_name, r.email, r.phone or ''] for r in records]
    elif model_name == 'Subject':
        headers = ["ID", "Назва", "Викладач"]
        data = [[r.id, r.name, r.teacher_id] for r in records]
    elif model_name == 'Grade':
        headers = ["ID", "Студент", "Предмет", "Оцінка", "Дата"]
        data = [[r.id, r.student_id, r.subject_id, r.grade, r.date_received] for r in records]
    else:
        
        if not records:
            return [], []
        
        sample_record = records[0]
        headers = [attr for attr in dir(sample_record) 
                  if not attr.startswith('_') and not callable(getattr(sample_record, attr))
                  and attr not in ('group', 'grades', 'metadata', 'registry')]
        data = [[getattr(r, attr) for attr in headers] for r in records]
    
    return headers, data

def main():
    
    parser = argparse.ArgumentParser(description='CRUD операції та звіти для моделей бази даних')
    
    parser.add_argument('-a', '--action', required=True, 
                        choices=['create', 'list', 'update', 'remove', 'report'],
                        help='CRUD операція або звіт: create, list, update, remove, report')
    
    parser.add_argument('-m', '--model', choices=['Student', 'Group', 'Teacher', 'Subject', 'Grade'],
                        help='Модель, над якою виконується операція (тільки для CRUD)')
    
    # ID для операцій update та remove
    parser.add_argument('--id', type=int, help='ID запису для операцій update та remove')    
        
    # Параметри для Student, Teacher
    parser.add_argument('--first_name', help='Ім\'я (для Student або Teacher)')
    parser.add_argument('--last_name', help='Прізвище (для Student або Teacher)')
    parser.add_argument('--email', help='Email (для Student або Teacher)')
    parser.add_argument('--phone', help='Телефон (для Student або Teacher)')
    parser.add_argument('--group_id', type=int, help='ID групи (для Student)')
    
    # Параметри для Group, Subject
    parser.add_argument('--name', help='Назва (для Group, Subject)')
    
    # Додаткові параметри для Subject
    parser.add_argument('--teacher_id', type=int, help='ID викладача (для Subject)')
    
    # Параметри для Grade
    parser.add_argument('--student_id', type=int, help='ID студента (для Grade)')
    parser.add_argument('--subject_id', type=int, help='ID предмету (для Grade)')
    parser.add_argument('--grade', type=float, help='Оцінка (для Grade)')
    parser.add_argument('--date_received', help='Дата оцінки у форматі YYYY-MM-DD (для Grade)')
    
    args = parser.parse_args()

   
    if args.action == 'report':
        reports_main()  
        return    
    
    if args.action in ['update', 'remove'] and args.id is None:
        parser.error(f"Операція {args.action} потребує аргументу --id")
    
    if args.action == 'create':
        # Видалення None значень та службових аргументів
        kwargs = {k: v for k, v in vars(args).items() 
                if v is not None and k not in ['action', 'model', 'id']}
        
        # Перевірка наявності необхідних аргументів для створення запису
        if args.model == 'Student':
            required_fields = ['first_name', 'last_name', 'email', 'phone', 'group_id']
            missing_fields = [field for field in required_fields if field not in kwargs]
            if missing_fields:
                parser.error(f"Для створення Student потрібні аргументи: {', '.join(['--' + f for f in missing_fields])}")
        elif args.model == 'Group' and 'name' not in kwargs:
            parser.error("Для створення Group потрібен аргумент --name")
        elif args.model == 'Teacher':
            required_fields = ['first_name', 'last_name', 'email', 'phone']
            missing_fields = [field for field in required_fields if field not in kwargs]
            if missing_fields:
                parser.error(f"Для створення Teacher потрібні аргументи: {', '.join(['--' + f for f in missing_fields])}")
        elif args.model == 'Subject' and ('name' not in kwargs or 'teacher_id' not in kwargs):
            parser.error("Для створення Subject потрібні аргументи --name та --teacher_id")
        elif args.model == 'Grade':
            required_fields = ['student_id', 'subject_id', 'grade', 'date_received']
            missing_fields = [field for field in required_fields if field not in kwargs]
            if missing_fields:
                parser.error(f"Для створення Grade потрібні аргументи: {', '.join(['--' + f for f in missing_fields])}")
    
        
        create_record(args.model, **kwargs)
    
    elif args.action == 'list':
        list_records(args.model)
    
    elif args.action == 'update':
        # Видалення None значень та службових аргументів
        kwargs = {k: v for k, v in vars(args).items() 
                if v is not None and k not in ['action', 'model', 'id']}
        
        if not kwargs:
            parser.error("Для операції update потрібно вказати хоча б один параметр для оновлення")
        
        update_record(args.model, args.id, **kwargs)
    
    elif args.action == 'remove':
        remove_record(args.model, args.id)

if __name__ == "__main__":
    main()