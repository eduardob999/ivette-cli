import urllib.request
import http.client
import json


def get_job_url(job_id):
    """
    Function to get URL for a given job_id
    """
    conn = http.client.HTTPConnection("localhost", 5328)
    conn.request("GET", f"/api/python/job/{job_id}")
    response = conn.getresponse()
    response_data = response.read().decode()
    if response_data:  # Check if response is not empty
        json_data = json.loads(response_data)
        if response.status == 200:
            return json_data
        else:
            raise ValueError(json_data.get('message', 'Unknown error'))  # More specific exception
    else:
        raise ValueError('Empty response from server')  # More specific exception


def get_next_job(dev=False):
    """
    Function to get the next job
    """
    path = "/api/python/get_next_job"
    if dev:
        conn = http.client.HTTPConnection("localhost", 5328)
    else:
        conn = http.client.HTTPSConnection("ivette-py.vercel.app")
    conn.request("GET", path)
    response = conn.getresponse()
    response_data = response.read().decode()
    if response_data:  # Check if response is not empty
        json_data = json.loads(response_data)
        if response.status == 200:
            return json_data
        else:
            # More specific exception
            raise ValueError(json_data.get('message', 'Unknown error'))
    else:
        # More specific exception
        raise ValueError('Empty response from server')


def retrieve_url(bucket, job_id, dev=False):
    """
    Retrieves the URL for the given bucket and job ID.
    If dev is True, uses the development environment.
    """
    path = "/api/python/next_job"
    if dev:
        conn = http.client.HTTPConnection("localhost", 5328)
    else:
        conn = http.client.HTTPSConnection("ivette-py.vercel.app")
    conn.request("GET", f"/api/python/retrieve_url/{bucket}/{job_id}")
    response = conn.getresponse()
    if response.status == 200:
        return response.read().decode()
    else:
        return None


def download_file(url, filename, *, dir='tmp/'):
    """
    Function to download a file from a given URL
    """
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url, filename)
