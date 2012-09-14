from neolib.neocodex.blowfish import Blowfish
import urllib
import urllib2
import random
import json

class CodexAPI:
    
    key = ""
    keyID = 0
    
    @staticmethod
    def setAuth(keyID, key):
        CodexAPI.keyID = keyID
        CodexAPI.key = key
    
    def priceItems(items):
        retItems = []
        sendItems = []
        for item in items:
            sendItems.append(item.name)
        
        resp = CodexAPI.searchMany(sendItems)
        
        for respItem in resp:
            retItems[respItem['name']].price = respItem['price']
            
        return retItems
    
    @staticmethod
    def searchOne(search, text):
        return CodexAPI._callAPI({'do': 'itemdb_read_one', 'search': search, 'value': text})
    
    @staticmethod
    def searchMany(items):
        return CodexAPI._callAPI({'do': 'itemdb_read_many', 'items': items})
        
    @staticmethod
    def _callAPI(data):
        if not isinstance(data, dict):
            raise TypeError, "API Calls can only happen with dictonary types."
        
        if not data.has_key("do"):
            raise NameError, "Missing the argument 'do' from the data."
        
        # Compile the items for the api in a random order.
        send_list = []
        for key, value in random.sample(data.items(), len(data)):
            # Lists and dicts cannot be transferd as str, use simplejson.dumps
            if isinstance(value, (list, dict)):
                value = json.dumps(value)
            
            send_list.append("%s=%s" % (key, urllib.quote(str(value))))
            
        send_encode = "&".join(send_list)
        
        # Encrypt the output using our key.
        bf = Blowfish(CodexAPI.key)
        bf.initCTR()
        send_data = bf.encryptCTR(str(send_encode)).encode('hex').upper()
        
        # Send and recieve the data
        req = urllib2.Request(url = "http://djangoapi.neocodex.us/api/do/?key_id=%i" % CodexAPI.keyID, data = 'encdata=' + send_data)
        h = urllib2.urlopen(req)

        # Turn the data back into an object.
        final_data = json.loads(h.read())
        return final_data