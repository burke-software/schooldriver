from django.conf import settings
import suds
import md5

class SugarSync:
    username = settings.SUGAR_USERNAME
    password = md5.md5(settings.SUGAR_PASSWORD).hexdigest()
    session = ''
    client = suds.client.Client(settings.SUGAR_URL + '/service/v2/soap.php?wsdl')
    
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
        )
        result = self.client.service.set_entry(
            session=self.session,
            module_name='Contacts',
            name_value_list=name_value_list,
        )
        if not contact.guid:
            contact.guid = result['id']
            contact.save(sync_sugar=False)