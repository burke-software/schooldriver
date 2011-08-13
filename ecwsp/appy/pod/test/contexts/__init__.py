# Here I define some classes that will be used for defining objects in several
# contexts.
class Person:
    def __init__(self, name):
        self.name = name
        self.lastName = '%s last name' % name
        self.firstName = '%s first name' % name
        self.address = '%s address' % name

class Group:
    def __init__(self, name):
        self.name = name
        if name == 'group1':
            self.persons = [Person('P1'), Person('P2'), Person('P3')]
        elif name == 'group2':
            self.persons = [Person('RA'), Person('RB')]
        else:
            self.persons = []
