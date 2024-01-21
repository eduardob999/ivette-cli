"""
Networking module for Ivette.
"""
import http.client
import json


# Methods definitions
def get_request(path, dev=False):
    host = "localhost:5328" if dev else "ivette-py.vercel.app"
    conn = http.client.HTTPSConnection(
        host) if not dev else http.client.HTTPConnection(host)
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


def post_request(path, data, headers, dev=False):
    host = "localhost:5328" if dev else "ivette-py.vercel.app"
    conn = http.client.HTTPSConnection(
        host) if not dev else http.client.HTTPConnection(host)
    conn.request("POST", path, body=json.dumps(data), headers=headers)
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


# Get methods
def get_next_job(dev=False):
    """
    Function to get the next job
    """
    return get_request("/api/python/get_next_job", dev=dev)


def retrieve_url(bucket, job_id, dev=False):
    """
    Retrieves the URL for the given bucket and job ID.
    If dev is True, uses the development environment.
    """
    host = "localhost:5328" if dev else "ivette-py.vercel.app"
    return get_request(f"/api/python/retrieve_url/{bucket}/{job_id}", dev=dev)


# Post methods
def update_job(job_id, status, nproc, species_id=None, dev=False):
    headers = {'Content-Type': 'application/json'}
    data = {
        'job_id': job_id,
        'status': status,
        'nproc': nproc,
        'species_id': species_id,
    }
    return post_request("/api/python/update_job", data, headers, dev)


# File management
def download_file(url, filename, *, dir='tmp/'):
    """
    Function to download a file from a given URL
    """
    host, path = url.split("/", 3)[2:]
    conn = http.client.HTTPSConnection(
        host) if "https" in url else http.client.HTTPConnection(host)
    conn.request("GET", "/" + path)
    response = conn.getresponse()
    if response.status == 200:
        with open(f"{dir}/{filename}", 'wb') as file:
            file.write(response.read())
    else:
        raise ValueError('Failed to download file')  # More specific exception
    conn.close()
