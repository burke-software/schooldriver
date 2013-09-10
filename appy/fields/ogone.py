# ------------------------------------------------------------------------------
import sha
from appy import Object
from appy.gen import Field
from appy.px import Px

# ------------------------------------------------------------------------------
class OgoneConfig:
    '''If you plan, in your app, to perform on-line payments via the Ogone (r)
       system, create an instance of this class in your app and place it in the
       'ogone' attr of your appy.gen.Config class.'''
    def __init__(self):
        # self.env refers to the Ogone environment and can be "test" or "prod".
        self.env = 'test'
        # You merchant Ogone ID
        self.PSPID = None
        # Default currency for transactions
        self.currency = 'EUR'
        # Default language
        self.language = 'en_US'
        # SHA-IN key (digest will be generated with the SHA-1 algorithm)
        self.shaInKey = ''
        # SHA-OUT key (digest will be generated with the SHA-1 algorithm)
        self.shaOutKey = ''

    def __repr__(self): return str(self.__dict__)

# ------------------------------------------------------------------------------
class Ogone(Field):
    '''This field allows to perform payments with the Ogone (r) system.'''
    urlTypes = ('accept', 'decline', 'exception', 'cancel')

    pxView = pxCell = Px('''<x>
     <!-- var "value" is misused and contains the contact params for Ogone -->
     <!-- The form for sending the payment request to Ogone -->
     <form method="post" id="form1" name="form1" var="env=value['env']"
           action=":'https://secure.ogone.com/ncol/%s/orderstandard.asp'% env">
       <input type="hidden" for="item in value.items()" if="item[0] != 'env'"
              id=":item[0]" name=":item[0]" value=":item[1]"/>
       <!-- Submit image -->
       <input type="image" id="submit2" name="submit2" src=":url('ogone.gif')"
              title=":_('custom_pay')"/>
     </form>
    </x>''')

    pxEdit = pxSearch = ''

    def __init__(self, orderMethod, responseMethod, show='view', page='main',
                 group=None, layouts=None, move=0, specificReadPermission=False,
                 specificWritePermission=False, width=None, height=None,
                 colspan=1, master=None, masterValue=None, focus=False,
                 mapping=None, label=None):
        Field.__init__(self, None, (0,1), None, show, page, group, layouts,
                       move, False, False,specificReadPermission,
                       specificWritePermission, width, height, None, colspan,
                       master, masterValue, focus, False, True, mapping, label,
                       None, None, None, None)
        # orderMethod must contain a method returning a dict containing info
        # about the order. Following keys are mandatory:
        #   * orderID   An identifier for the order. Don't use the object UID
        #               for this, use a random number, because if the payment
        #               is canceled, Ogone will not allow you to reuse the same
        #               orderID for the next tentative.
        #   * amount    An integer representing the price for this order,
        #               multiplied by 100 (no floating point value, no commas
        #               are tolerated. Dont't forget to multiply the amount by
        #               100!
        self.orderMethod = orderMethod
        # responseMethod must contain a method accepting one param, let's call
        # it "response". The response method will be called when we will get
        # Ogone's response about the status of the payment. Param "response" is
        # an object whose attributes correspond to all parameters that you have
        # chosen to receive in your Ogone merchant account. After the payment,
        # the user will be redirected to the object's view page, excepted if
        # your method returns an alternatve URL.
        self.responseMethod = responseMethod

    noShaInKeys = ('env',)
    noShaOutKeys = ('name', 'SHASIGN')
    def createShaDigest(self, values, passphrase, keysToIgnore=()):
        '''Creates an Ogone-compliant SHA-1 digest based on key-value pairs in
           dict p_values and on some p_passphrase.'''
        # Create a new dict by removing p_keysToIgnore from p_values, and by
        # upperizing all keys.
        shaRes = {}
        for k, v in values.iteritems():
            if k in keysToIgnore: continue
            # Ogone: we must not include empty values.
            if (v == None) or (v == ''): continue
            shaRes[k.upper()] = v
        # Create a sorted list of keys
        keys = shaRes.keys()
        keys.sort()
        shaList = []
        for k in keys:
            shaList.append('%s=%s' % (k, shaRes[k]))
        shaObject = sha.new(passphrase.join(shaList) + passphrase)
        res = shaObject.hexdigest()
        return res

    def getValue(self, obj):
        '''The "value" of the Ogone field is a dict that collects all the
           necessary info for making the payment.'''
        tool = obj.getTool()
        # Basic Ogone parameters were generated in the app config module.
        res = obj.getProductConfig(True).ogone.copy()
        shaKey = res['shaInKey']
        # Remove elements from the Ogone config that we must not send in the
        # payment request.
        del res['shaInKey']
        del res['shaOutKey']
        res.update(self.callMethod(obj, self.orderMethod))
        # Add user-related information
        res['CN'] = str(tool.getUserName(normalized=True))
        user = obj.appy().appyUser
        res['EMAIL'] = user.email or user.login
        # Add standard back URLs
        siteUrl = tool.getSiteUrl()
        res['catalogurl'] = siteUrl
        res['homeurl'] = siteUrl
        # Add redirect URLs
        for t in self.urlTypes:
            res['%surl' % t] = '%s/onProcess' % obj.absolute_url()
        # Add additional parameter that we want Ogone to give use back in all
        # of its responses: the name of this Appy Ogone field. This way, Appy
        # will be able to call method m_process below, that will process
        # Ogone's response.
        res['paramplus'] = 'name=%s' % self.name
        # Ensure every value is a str
        for k in res.iterkeys():
            if not isinstance(res[k], str):
                res[k] = str(res[k])
        # Compute a SHA-1 key as required by Ogone and add it to the res
        res['SHASign'] = self.createShaDigest(res, shaKey,
                                              keysToIgnore=self.noShaInKeys)
        return res

    def ogoneResponseOk(self, obj):
        '''Returns True if the SHA-1 signature from Ogone matches retrieved
           params.'''
        response = obj.REQUEST.form
        shaKey = obj.getProductConfig(True).ogone['shaOutKey']
        digest = self.createShaDigest(response, shaKey,
                                      keysToIgnore=self.noShaOutKeys)
        return digest.lower() == response['SHASIGN'].lower()

    def process(self, obj):
        '''Processes a response from Ogone.'''
        # Call the response method defined in this Ogone field.
        if not self.ogoneResponseOk(obj):
            obj.log('Ogone response SHA failed. REQUEST: %s' % \
                    str(obj.REQUEST.form))
            raise Exception('Failure, possible fraud detection, an ' \
                            'administrator has been contacted.')
        # Create a nice object from the form.
        response = Object()
        for k, v in obj.REQUEST.form.iteritems():
            setattr(response, k, v)
        # Call the field method that handles the response received from Ogone.
        url = self.responseMethod(obj.appy(), response)
        # Redirect the user to the correct page. If the field method returns
        # some URL, use it. Else, use the view page of p_obj.
        if not url: url = obj.absolute_url()
        obj.goto(url)
# ------------------------------------------------------------------------------
