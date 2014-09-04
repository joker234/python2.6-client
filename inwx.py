#!/usr/bin/env python
# -*- encoding: UTF8 -*-

# author: Philipp Klaus, philipp.klaus →AT→ gmail.com
# author: InterNetworX, info →AT→ inwx.de

# This file is part of python-inwx-xmlrpc.
#
# python-inwx-xmlrpc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-inwx-xmlrpc is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-inwx-xmlrpc. If not, see <http://www.gnu.org/licenses/>.


#####################################################################
###### This the most important file of the project: #######

from xmlrpclib import ServerProxy, Fault, ProtocolError, _Method, SafeTransport
from os import path

class domrobot (ServerProxy):
    def __init__ (self, address, verbose=False):
        self.__address = address
        ServerProxy.__init__(self, address, transport=InwxTransport(), encoding = "UTF-8", verbose=verbose)

    def __getattr__(self,name):
        return _Method(self.__request, name)

    def __request (self, methodname, params):
        method_function = ServerProxy.__getattr__(self,methodname)
        self.__params = dict()

        if len(params)>0 and type(params[0]) is dict: self.__params.update(params[0])
        try:
            response = method_function(self.__params)
        except Fault, err:
            raise NameError("Fault", err)
        except ProtocolError, err:
            raise NameError("ProtocolError", err)
        except Exception, err:
            raise NameError("Some other error occured, presumably with the network connection to %s" % self.__address, err)
        if response['code'] < 2000:
            try:
                return response['resData']
            except:
                # not all requests send a response
                return None
        else:
            raise NameError('There was a problem: %s (Error code %s)' % (response['msg'], response['code']), response)

class InwxTransport(SafeTransport):
    user_agent = "DomRobot/1.0 Python-v2.6"
    
    def request(self, host, handler, request_body, verbose=0):
        # issue XML-RPC request
        h = self.make_connection(host)
        if verbose:
            h.set_debuglevel(1)

        self.send_request(h, handler, request_body)
        self.send_host(h, host)
        self.send_user_agent(h)
        self.send_content(h, request_body)

        errcode, errmsg, headers = h.getreply()

        if errcode != 200:
            raise ProtocolError(
                host + handler,
                errcode, errmsg,
                headers
                )

        self.setCookie(headers.getheaders('set-cookie'))

        self.verbose = verbose

        try:
            sock = h._conn.sock
        except AttributeError:
            sock = None

        return self._parse_response(h.getfile(), sock)     
    
    def setCookie(self,cookie):
        if len(cookie)>0:
            fp = open("domrobot.tmp", "w")
            fp.write(cookie[0])
            fp.close()
        
    def getCookie(self):
        cookie = ""
        file = "domrobot.tmp"
        if path.exists(file):
            fp = open(file, "r")
            cookie = fp.read()
            fp.close()
        return cookie

    def send_content(self, connection, request_body):
        connection.putheader("Content-Type", "text/xml")
        connection.putheader("Content-Length", str(len(request_body)))
        cookie = self.getCookie()
        if len(cookie)>2:
            connection.putheader("Cookie", cookie)
            
        connection.endheaders()
        if request_body:
            connection.send(request_body)

class prettyprint (object):
    """
    This object is just a collection of prettyprint helper functions for the output of the XML-API.
    """

    @staticmethod
    def contacts(contacts):
        """
        iterable contacts:  The list of contacts to be printed.
        """
        output = "\nCurrently you have %i contacts set up for your account at InterNetworX:\n\n" % len(contacts)
        for contact in contacts:
            output += "ID: %s\nType: %s\n%s\n%s\n%s %s\n%s\n%s\nTel: %s\n------\n" % (contact['id'], contact['type'], contact['name'], contact['street'], contact['pc'], contact['city'], contact['cc'], contact['email'], contact['voice'])
        return output

    @staticmethod
    def domains(domains):
        """
        list domains:  The list of domains to be pretty printed.
        """
        output = "\n%i domains:\n" % len(domains)
        for domain in domains:
            output += "Domain: %s (Type: %s)\n" % (domain['domain'], domain['type'])
        return output

    @staticmethod
    def nameserversets(nameserversets):
        """
        list namerserversets:  The list of nameserversets to be pretty printed.
        """
        count, total = 0, len(nameserversets)
        output = "\n%i nameserversets:\n" % total
        for nameserverset in nameserversets:
            count += 1
            output += "%i of %i - ID: %i consisting of [%s]\n" % (count, total, nameserverset['id'], ", ".join(nameserverset['ns']))
        return output

    @staticmethod
    def domain_log(logs):
        """
        list logs:  The list of nameserversets to be pretty printed.
        """
        count, total = 0, len(logs)
        output = "\n%i log entries:\n" % total
        for log in logs:
            count += 1
            output += "%i of %i - %s status: '%s' price: %.2f invoice: %s date: %s remote address: %s\n" % (count, total, log['domain'], log['status'], log['price'], log['invoice'], log['date'], log['remoteAddr'])
            output += "           user text: '%s'\n" % log['userText'].replace("\n",'\n           ')
        return output
    
    @staticmethod
    def domain_check(checks):
        """
        list checks:  The list of domain checks to be pretty printed.
        """
        count, total = 0, len(checks)
        output = "\n%i domain check(s):\n" % total
        for check in checks['domain']:
            count += 1
            output += "%s = %s" % (check['domain'], check['status'])
        return output
        