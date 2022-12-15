import io
import sys
import json
from typing import TextIO


class Person:
    def __init__(self, name: str, birthday: str, person_id: int, *args, **kwargs):
        self.name = name
        self.birthday = birthday
        self.person_id = person_id

    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def init_from_json(cls, json_str: str | dict):
        new_instance = cls.__new__(cls)
        kwargs = json.loads(json_str) if isinstance(json_str, str) else json_str
        new_instance.__init__(**kwargs)
        return new_instance

    @property
    def key(self):
        return self.name, self.birthday, self.person_id

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.key == other.key
        return NotImplemented



class Student(Person):
    def __init__(self, name: str, birthday: str, person_id: int, department: str, group: int, student_id: int,
                 *args, **kwargs):
        super().__init__(name, birthday, person_id, *args, **kwargs)
        self.department = department
        self.group = group
        self.student_id = student_id

    def __str__(self):
        return f'Student {self.name} from group {self.group}, {self.department}'

    @property
    def key(self):
        return super().key + (self.student_id, )


class Teacher(Person):
    def __init__(self, name: str, birthday: str, person_id: int, course: str, groups: list, students: list,
                 *args, **kwargs):
        super().__init__(name, birthday, person_id, *args, **kwargs)
        self.course = course
        self.groups = groups
        self.students = students

    def __str__(self):
        return f'Teacher {self.name} on course {self.course}. Works ' \
        f'with {len(self.groups)} groups and {len(self.students)} students.'

class AssistantStudent(Student, Teacher, Person):
    def __init__(self, name: str, birthday: str, person_id: int, department: str, group: int, student_id: int,
                 course: str, groups: list, students: list):
        super().__init__(name, birthday, person_id, department, group, student_id, course, groups, students)

    def __str__(self):
        return f'Student {self.name} from group {self.group}, {self.department}. Also teaches ' \
               f'{self.course} in {len(self.groups)} groups and mentors {len(self.students)} students.'

def get_entities(db: TextIO) -> str:
    for record in db.readlines():
        init_dict = json.loads(record)
        dict_length = len(init_dict)
        if dict_length == 3:
            entity_class = Person
        elif dict_length == 6:
            entity_class = Teacher if 'students' in init_dict else Student
        elif dict_length == 9:
            entity_class = AssistantStudent
        else:
            raise ValueError(f'Incorrect record in database: {dict_length} fields get')
        init_dict['person_id'] = init_dict.pop('id')
        # # LOGS
        # entity = entity_class.init_from_json(init_dict)
        # print(entity_class, entity)
        yield entity_class.init_from_json(init_dict)

def just_read(db: TextIO, output: TextIO) -> None:
    for entity in get_entities(db):
        print(entity, file=output)

def field_is_arg(field: str, arg: str, db: TextIO, output: TextIO) -> None:
    arg = arg.strip('"')
    for entity in get_entities(db):
        if hasattr(entity, field):
            if arg in (str(getattr(entity, field)), 'set'):
                print(entity, file=output)

def field_in_args(field: str, args: list, db: TextIO, output: TextIO) -> None:
    collection = set(map(lambda x: x.strip('{}", '), args))
    for entity in get_entities(db):
        if hasattr(entity, field) and str(getattr(entity, field)) in collection:
            print(entity, file=output)

def field_contains_arg(field: str, arg, db: TextIO, output: TextIO) -> None:
    arg = arg.strip('"')
    for entity in get_entities(db):
        if hasattr(entity, field) and str(arg) in str(getattr(entity, field)):
            print(entity, file=output)

def solution(requests: TextIO, db_name: str, output: TextIO) -> None:
    for request in requests.readlines():
        with open(db_name, 'r') as db:
            try:
                tokens = request.split()
                if tokens == ['get', 'records']:
                    cond = '<no commands>'
                else:
                    field, cond, args = tokens[3], tokens[4], tokens[5:]
                match cond:
                    case '<no commands>':
                        just_read(db=db, output=output)
                    case 'is':
                        field_is_arg(field=field, arg=args[0], db=db, output=output)
                    case 'in':
                        field_in_args(field=field, args=args, db=db, output=output)
                    case 'contains':
                        field_contains_arg(field=field, arg=args[0], db=db, output=output)
                    case _:
                        print(f'unknown command "{request}"', file=output)
            except ValueError as invalid_input:
                print(f'Invalid input: {invalid_input}')
            except IndexError as invalid_input:
                print(f'Invalid input (maybe command is too short): {invalid_input}')


if __name__ == '__main__':
    print('$ ', end='')
    for line in sys.stdin:
        solution(io.StringIO(line.strip()), 'db.txt', sys.stdout)
        print('$ ', end='')

