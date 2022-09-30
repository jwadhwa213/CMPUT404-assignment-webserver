#  coding: utf-8 
import socketserver
import os
import mimetypes
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime


# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        message_200= "HTTP/1.1 200 OK"
        message_404 = "HTTP/1.1 404 Not Found!" 
        message_405 = "HTTP/1.1 405 Method Not Allowed" 
        message_301 = "HTTP/1.1 301 Moved Permanently" 


        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        method, path, *rest = self.data.decode('utf-8').split(" ")
        

        absolute_path = f"./www{path}"
    
        if method != 'GET':
            httpResponse = self.format_response(message_405)

        elif os.path.isdir(absolute_path) and not path.endswith('/'):
            httpResponse = self.format_response(message_301, location = f"{path}/")

        elif not(os.path.realpath(f"./www{path}").startswith(os.path.realpath("./www"))):
            print(os.path.realpath(f"./www{path}"))
            httpResponse = self.format_response(message_404)

        elif not os.path.exists(absolute_path):
            print("404 Not Found")
            httpResponse = self.format_response(message_404)
        else:
            if os.path.isdir(absolute_path):
                absolute_path += 'index.html'
            file = open(absolute_path, 'r')
            size = os.path.getsize(absolute_path)
            lines = file.read()
            file.close()
            content={
                'content' : lines,
                'length' : os.path.getsize(absolute_path),
                'type' : mimetypes.guess_type(absolute_path, strict = True)[0]
            }
            httpResponse = self.format_response(message_200, content = content)
        self.request.sendall(bytearray(httpResponse,'utf-8'))

    def format_response(self, message, content = None, location = None):

        response = f"{message}\r\n"

        dateTime_now = datetime.now()
        timeStamp = mktime(dateTime_now.timetuple())

        response += f"Date: {format_date_time(timeStamp)}\r\n"
        response += f"Connection: Closed\r\n"
        # response += f"Server: Apache/2.2.14 (Win32)\r\n"

        if not location == None :
            response += f"Location: {location}\r\n"
        if not content == None :
            response += f"Content-Type: {content['type']}\r\n"
            response += f"Content-Length: {content['length']}\r\n"
            response += f"\r\n{content['content']}"

        
        return response

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
