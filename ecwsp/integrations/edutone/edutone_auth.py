"""
This backend adds support for login from Edutone Passport. The settings
EDUTONE_SECRET_KEY and EDUTONE_ENCRYPTION_KEY must be defined with the values
given by Edutone.
"""

from social.backends.base import BaseAuth
from social.exceptions import AuthMissingParameter, AuthException
from django.utils import datastructures
from locale import str
from hashlib import sha1
from Crypto.Cipher import AES
import time
import hmac
import binascii
import base64

class EdutoneAuth(BaseAuth):
    name = 'edutone'
    ID_KEY = 'username'
    
    def get_user_id(self, details, response):
        return details.get(self.ID_KEY) or \
               response.get(self.ID_KEY)

    def auth_url(self):
        return None

    def auth_html(self):
        return None

    def uses_redirect(self):
        return False

    def auth_complete(self, *args, **kwargs):
        """Completes loging process, must return user instance"""

         # validate signature
        ts = int(self.data.get('ts', ''))
        sig = self.data.get('sig', '')
        self.validateSignature(ts, sig)
                
         # decrypt userData using AES
        iv = self.data.get('iv', '')
        userDataEnc = self.data.get('userData', '')
        userData = self.decrypt(userDataEnc, iv)

        userData = userData.replace('\"', '')
        
        userDataList = userData.split(',')
        
        userDataDict = {'username':userDataList[0]}
        userDataDict['first_name'] = userDataList[1]
        userDataDict['last_name'] = userDataList[2]
        userDataDict['email'] = userDataList[3]
        
        self.data = datastructures.MergeDict(self.data, userDataDict)
        
        if self.ID_KEY not in self.data:
            raise AuthMissingParameter(self, self.ID_KEY)
        kwargs.update({'response': self.data, 'backend': self})
        return self.strategy.authenticate(*args, **kwargs)

    def get_user_details(self, response):
        """Return user details"""
        email = response.get('email', '')
        username = response.get('username', '')
        first_name = response.get('first_name', '')
        last_name = response.get('last_name', '')
        
        if not username and first_name and last_name:
            username = first_name + last_name
        
        if first_name and last_name:
            fullname = first_name + ' ' + last_name
        
        return {
            'username': username,
            'email': email,
            'fullname': fullname,
            'first_name': first_name,
            'last_name': last_name
        }
        
    def validateSignature(self, ts, sig):
        current_ts = int(time.time())
        signature_life = self.setting('EDUTONE_SIGNATURE_LIFE') or 10
        if ts + signature_life < current_ts or ts > current_ts:
            raise AuthException(self, 'Signature is expired.')
        
        secretKey = self.setting('EDUTONE_SECRET_KEY')
        
        hashed = hmac.new(base64.b64decode(secretKey), str(ts), sha1)
        check_signature = binascii.b2a_base64(hashed.digest())[:-1]
        
        if check_signature != sig:
            raise AuthException(self, 'Invalid sugnature.')

    def decrypt(self, userDataEnc, iv):
        unpad = lambda s : s[0:-ord(s[-1])]
        
        userDataEnc = base64.b64decode(userDataEnc)
        iv = base64.b64decode(iv)
        encryptionKey = self.setting('EDUTONE_ENCRYPTION_KEY')
        
        cipher = AES.new(base64.b64decode(encryptionKey), AES.MODE_CBC, iv)
        
        return unpad(cipher.decrypt(userDataEnc))
    