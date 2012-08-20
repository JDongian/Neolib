import re
from datetime import datetime
import logging

class Cookie:
    name = ""
    value = ""
    expires = ""
    path = ""
    domain = ""
    
    def __init__(self, cookieStr):
        # Temporary fix
        cookieStr += "\r"
        
        try:
            mat = re.match("(.*)=(.*); expires=(.*); path=(.*); domain=(.*?)\r", cookieStr)
        
            self.name = mat.group(1)
            self.value = mat.group(2)
            self.expires = mat.group(3)
            self.path = mat.group(4)
            self.domain = mat.group(5)
        except Exception:
            logging.getLogger("neolib").exception("Failed to parse cookie string: " + cookieStr)
        
    def isExpired(self):
        if datetime.now() < datetime.strptime(self.expires, "%a, %d-%b-%Y %H:%M:%S %Z"):
            return False
        else:
            return True
    
    def toStr(self):
        return self.name + "=" + self.value + ";"