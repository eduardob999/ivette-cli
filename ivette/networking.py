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
    if response.status == 200:
        return json.loads(response.read().decode())
    else:
        return None


def get_next_job():
    """
    Function to get the next job
    """
    conn = http.client.HTTPConnection("localhost", 5328)
    conn.request("GET", "/api/python/next_job")
    response = conn.getresponse()
    if response.status == 200:
        return json.loads(response.read().decode())
    else:
        return None


def download_file(url, filename):
    """
    Function to download a file from a given URL
    """
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url, filename)
