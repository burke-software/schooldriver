class Student:
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

students = [
   Student(parent_guardian='Parent 1', street='Street 1', city='Flawinne',
           state='Namur', zip='5020', lname='Name 1', fname='First name 1'),
   Student(parent_guardian='Parent 2', street='Street 2', city='Flawinne',
           state='Namur', zip='5020', lname='Name 2', fname='First name 2'),
   Student(parent_guardian='Parent 3', street='Street 3', city='Flawinne',
           state='Namur', zip='5020', lname='Name 3', fname='First name 3'),
   Student(parent_guardian='Parent 4', street='Street 4', city='Flawinne',
           state='Namur', zip='5020', lname='Name 4', fname='First name 4'),
   Student(parent_guardian='Parent 5', street='Street 5', city='Flawinne',
           state='Namur', zip='5020', lname='Name 5', fname='First name 5'),
]
