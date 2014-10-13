__author__ = "ghermeto"
__date__ = "$27/07/2011 23:23:17$"

import json
import time
try:
    from http.client import HTTPSConnection
except ImportError:
    from httplib import HTTPSConnection


class Error(Exception):
    """ Base error for Blitz api. """

    def __init__(self, error, reason):
        self.error = error
        self.reason = reason

    def __str__(self):
        return 'Error({}, {})'.format(self.error, self.reason)


class ValidationError(Error):
    """ Validation error for Blitz api. """
    
    def __init__(self, reason, fields = []):
        self.error = "validation"
        self.reason = reason
        self.fields = fields

class Client:
    """ Responsable for requests to Blitz RESTful API """
    
    def __init__(self, user, api_key, host=None, port=None, connect=True):
        self.username = user
        self.api_key = api_key
        self.host = 'www.blitz.io' if host is None else host
        self.port = 443 if port is None else port
        self.private_key = None
        if connect:
            self.connect()
    
    def connect(self):
        """ Connects the client. """
        self.connection = HTTPSConnection(self.host, self.port)

    def get_headers(self):
        """ Returns the headers need for a auccessful request to blitz.io. """
        private = self.private_key
        headers = {
            "Content-type": "application/json",
            'X-API-User': self.username, 
            'X-API-Key': self.api_key if private is None else private,
            'X-API-Client' : 'python'
        }
        return headers
    
    def set_private_key(self, key):
        """ Sets the user private key to be used in the request header.  """
        self.private_key = key
    
    def execute(self, post_data):
        """ Sends a queue request to blitz.io RESTful API. """
        path = "/api/1/curl/execute"
        data = json.dumps(post_data)
        self.connection.request("POST", path, data, self.get_headers())
        response = self.connection.getresponse()
        response_string = response.read().decode('UTF-8')
        return json.loads(response_string)
    
    def login(self):
        """ Login to blitz.io RESTful API. """
        path = "/login/api"
        self.connection.request("GET", path, None, self.get_headers())
        response = self.connection.getresponse()
        response_string = response.read().decode('UTF-8')
        return json.loads(response_string)
    
    def job_status(self, job_id):
        """ Sends a job status request to blitz.io  RESTful API. """
        path = "/api/1/jobs/{}/status".format(job_id)
        self.connection.request("GET", path, None, self.get_headers())
        response = self.connection.getresponse()
        response_string = response.read().decode('UTF-8')
        return json.loads(response_string)
    
    def abort_job(self, job_id):
        """ Send a abort request to blitz.io RESTful API. """
        path = "/api/1/jobs/{}/abort".format(job_id)
        self.connection.request("PUT", path, '', self.get_headers())
        response = self.connection.getresponse()
        response_string = response.read().decode('UTF-8')
        return json.loads(response_string)
    
    def close(self):
        """ Closes the connection. """
        self.connection.close()
        
    def parse(self, post_data):
        """ Sends a parse request to blitz.io RESTful API. """
        path = "/api/1/parse"
        data = json.dumps(post_data)
        self.connection.request("POST", path, data, self.get_headers())
        response = self.connection.getresponse()
        response_string = response.read().decode('UTF-8')
        return json.loads(response_string)

class Curl:
    """ Base class used by Blitz curl tests. """
    
    def __init__(self, user, api_key, host=None, port=None, connect=True):
        self.client = Client(user, api_key, host, port, connect)
        self.job_id = None
        
    def execute(self, options, callback):
        """ Execute the test and waits for job_status notifications from the
            server. """
        self._validate(options) # raises error if options isn't valid
        self._check_authentication() #authenticates
        queue_response = self.client.execute(options)
        self._check_errors(queue_response)
        self.job_id = queue_response['job_id']
        self.job_status(callback)
    
    def job_status(self, callback):
        """ Make a job status request to blitz every two seconds and tirggers
            the callback on successful responses. Raise an error otherwise. """
        if self.job_id is None:
            raise Error('client', 'No job')
        self._check_authentication() #authenticates
        status = None
        while status != 'completed':
            time.sleep(2)
            job = self.client.job_status(self.job_id)
            if job is None:
                raise Error('client', 'No response') 
            elif 'status' not in job:
                raise Error('client', 'Wrong response format') 
            elif 'error' in job:
                raise Error(job['error'], job['reason'])
            elif 'result' in job and 'error' in job['result']:
                raise Error(job['result']['error'], job['result']['reason'])
            elif job['status'] == 'queued' \
            or (job['status'] == 'running' and not 'result' in job):
                continue
            result = self._format_result(job['result'])
            callback(result)
            status = job['status']
    
    def _validate(self, options):
        """ Method should be overriden by subclasses and raise a ValidationError
            if validation fails. """
        pass
    
    def _format_result(self, result):
        """ Method should be overriden by subclasses and return the appropritate
            result object to be passed to the callback. """
        pass
    
    def _check_errors(self, response):
        """ Raise the proper error if server return a failure message. """
        if response is None:
            raise Error('client', 'No response')
        elif 'error' in response:
            raise Error(response['error'], response['reason'])
    
    def _check_authentication(self):
        """ Authenticates the Client if necesary, storing the private key. """
        if self.client.private_key is None: 
            response = self.client.login()
            if response is None:
                raise Error('client', 'No response') 
            elif 'error' in response:
                raise Error(response['error'], response['reason'])
            else:
                self.client.set_private_key(response['api_key'])
    
    def abort(self):
        """ Aborts the current job. """
        try:
            self.client.abort_job(self.job_id)
        except:
            pass