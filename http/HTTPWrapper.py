from HTTPRequestHeader import HTTPRequestHeader
from HTTPResponseHeader import HTTPResponseHeader
from urlparse import urlparse
from CookieJar import CookieJar
from Cookie import Cookie
import socket
import zlib
import logging

class HTTPWrapper:
    sock = None
    repHeader = None
    repContent = ""
    cookieJar = None
    
    timeout = 15.00
    
    logger = None
    
    def __init__(self):
        # Setup a logger instance for debugging use
        if not self.logger:
            self.logger = logging.getLogger("neolib")
    
    def request(self, type, url, postData = "", vars = None):
        # Create a socket to use
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Set a 15 second timeout so operations won't hang
        s.settimeout(self.timeout)
        
        # Parse the URL to determine what exactly we're doing
        parsedUrl = urlparse(url)
        
        # Grab any cookies
        if self.cookieJar:
            cookies = self.cookieJar.getCookies()
        else:
            cookies = ""
        
        # Let's build a request header before connecting
        rHeader = HTTPRequestHeader(type, parsedUrl.netloc, parsedUrl.path + "?" + parsedUrl.query, cookies, postData, vars)
        
        # Now we can connect and send the request
        try:
            s.connect((parsedUrl.netloc, 80))
        except Exception:
            errMsg = "Failed to connect to host: %s on port 80", parsedURL.netloc
            self.logger.exception(errMsg)
            raise Exception
            
        
        # Send the request
        s.sendall(rHeader.headerContent)
        
        # Now begin buffering the response
        # 16384 is a mid-sized buffer and is divisible by 2, thus making it an ideal choice
        try:
            data = s.recv(16384)
        
            while True:
                more = s.recv(16384)
                if not more:
                    break
                else:
                    data += more
        except socket.timeout:
            errMsg = "Connection timed-out while connecting to %s. Request headers were as follows: %s", (parsedURL.netloc, rHeader.headerContent)
            self.logger.exception(errMsg)
            raise Exception
            
        # Don't forget to close your sockets!
        s.close()
        
        # Split the response header and content
        header, content = data.split("\r\n\r\n")
        
        # Parse the headers for future usage
        self.repHeader = HTTPResponseHeader(header)
        
        # Update cookies
        self.cookieJar = CookieJar(self.repHeader.cookies)
        
        # If the content was gzip encoded, decode it
        if self.repHeader.respVars['Content-Encoding'].find("gzip") != -1:
            self.repContent = zlib.decompress(content, 16+zlib.MAX_WBITS)
        else:
            self.repContent = content
        
        # Return the content        
        return self.repContent
        