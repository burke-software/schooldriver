from constance import config
from django.core.exceptions import SuspiciousOperation
from ecwsp.administration.models import Configuration
from ecwsp.work_study.models import Contact
import HTMLParser
import suds
import md5
import datetime

class SugarSync:
    if config.SUGAR_SYNC:
        username = config.SUGAR_USERNAME
        password = md5.md5(config.SUGAR_PASSWORD).hexdigest()
        session = ''
        client = suds.client.Client(config.SUGAR_URL + '/service/v2/soap.php?wsdl', location=config.SUGAR_URL + '/service/v2/soap.php')

        def __init__(self):
            self.login()

        def login(self):
            """ Log in to sugarcrm as a admin user and
            store the session id
            """
            result = self.client.service.login(user_auth={
                'user_name':self.username,
                'password':self.password,
            })
            self.session = result['id']

        def update_contact(self,contact):
            """ create or update a contact in sugarcrm
            contact: a django-sis.work_study contact who we want to
            create or update in sugarcrm
            """
            name_value_list = ()
            if contact.guid:
                name_value_list += ({'name':'id','value':contact.guid},)
            name_value_list += (
                {'name':'first_name','value':contact.fname},
                {'name':'last_name','value':contact.lname},
                {'name':'title','value':contact.title},
                {'name':'phone_work','value':contact.phone},
                {'name':'phone_mobile','value':contact.phone_cell},
                {'name':'phone_fax','value':contact.fax},
                {'name':'email1','value':contact.email},
                {'name':'deleted','value':'0'},
                {'name':'supervisor_c','value':'1'},
            )
            result = self.client.service.set_entry(
                session=self.session,
                module_name='Contacts',
                name_value_list=name_value_list,
            )
            if not contact.guid:
                contact.guid = result['id']
                contact.save(sync_sugar=False)

        def update_contacts_from_sugarcrm(self):
            """ Query recently changed contacts in SugarCRM and sync them to django-sis
            """
            modify_date_minutes = config.SUGAR_SYNC_MINUTES
            modify_date = datetime.datetime.now() - datetime.timedelta(minutes=modify_date_minutes + 1)
            contacts = self.get_recent_sugar_contacts(modify_date)
            for contact in contacts:
                self.set_django_sis_contact(contact)

        def get_recent_sugar_contacts(self, modify_date=None):
            """ Get a list of recently updated sugarcrm contacts
            modify_date: find contacts modified after this datetime
            defaults to one hour ago
            returns list of contact data
            """
            if not modify_date:
                modify_date = datetime.datetime.now() - datetime.timedelta(hours=1)
            elif not isinstance(modify_date, datetime.datetime):
                raise SuspiciousOperation('Date that is not a date. Possible SQL injection attempt?')

            result = self.client.service.get_entry_list(
                session=self.session,
                module_name='Contacts',
                query='supervisor_c = 1 and contacts.date_modified > "%s"' % (str(modify_date),)
            )
            return result[2]

        def set_django_sis_contact(self, contact):
            """ Set django-sis contact from sugarcrm contact data
            """
            guid = contact[0]

            if Contact.objects.filter(guid=guid):
                sis_contact = Contact.objects.get(guid=guid)
            else:
                sis_contact = Contact(guid=guid)
            h = HTMLParser.HTMLParser()
            for field in contact[2]:
                if field.value:
                    # HTML unescape
                    field.value = h.unescape(field.value)
                    if field.name == "first_name":
                        sis_contact.fname = field.value
                    elif field.name == "last_name":
                        sis_contact.lname = field.value
                    elif field.name == "title":
                        sis_contact.title = field.value
                    elif field.name == "phone_work":
                        sis_contact.phone = field.value
                    elif field.name == "phone_mobile":
                        sis_contact.phone_cell = field.value
                    elif field.name == "phone_fax":
                        sis_contact.fax = field.value
                    elif field.name == "email1":
                        sis_contact.email = field.value

            sis_contact.save(sync_sugar=False)
