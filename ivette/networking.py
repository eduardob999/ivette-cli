"""
Networking module for Ivette.
"""
# Standard library imports
import http.client
import json
import mimetypes
import os
from typing import Optional

# Local application/library specific imports
from ivette.utils import trim_file


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
def get_next_job(memory, nproc,  dev=False):
    """
    Function to get the next job
    """
    return get_request(f"/api/python/get_next_job/{memory}/{nproc}", dev=dev)


def get_temp_filenames(bucket: str, prefix: str,  dev=False):
    """
    Retrieves an array with filenames from the given bucket and prefix.
    """
    return get_request(f"/api/python/get_temp_filenames/{bucket}/{prefix}", dev=dev)


def retrieve_url(bucket, job_id, dev=False):
    """
    Retrieves the URL for the given bucket and job ID.
    If dev is True, uses the development environment.
    """
    return get_request(f"/api/python/retrieve_url/{bucket}/{job_id}", dev=dev)


def retrieve_signed_url(bucket, job_id, dev=False):
    """
    Retrieves the signed URL for the given bucket and job ID.
    If dev is True, uses the development environment.
    """
    return get_request(f"/api/python/retrieve_signed_url/{bucket}/{job_id}", dev=dev)


# Post methods
def update_job(job_id, status, nproc, species_id=None, dev=False, **kwargs):
    headers = {'Content-Type': 'application/json'}
    data = {
        'job_id': job_id,
        'status': status,
        'nproc': nproc,
        'species_id': species_id,
    }
    data.update(kwargs)
    return post_request("/api/python/update_job", data, headers, dev)


def delete_file(bucket, filename, dev=False, **kwargs):
    """
    Function to delete a file from the given bucket
    """
    headers = {'Content-Type': 'application/json'}
    data = {
        "bucket": bucket,
        "filename": filename
    }
    data.update(kwargs)
    return post_request("/api/python/delete_file", data, headers, dev)


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


def upload_file(file_path: str, instruction: Optional[str] = None, dev: bool = False) -> str:
    """
    Function to upload a file to the server.

    Args:
        file_path (str): The path to the file to be uploaded.
        instruction (str, optional): Additional instruction for the server. Defaults to None.
        dev (bool, optional): Whether to use the development environment. Defaults to False.
        trim_size (int, optional): The size to trim the file to. Defaults to 25.

    Returns:
        str: The response from the server.

    Raises:
        ValueError: If the file upload fails.
    """
    filename = os.path.basename(file_path)
    host = "localhost:5328" if dev else "ivette-py.vercel.app"
    path = "/api/python/upload_file"
    conn = http.client.HTTPSConnection(
        host) if not dev else http.client.HTTPConnection(host)

    boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
    headers = {'Content-Type': 'multipart/form-data; boundary=%s' % boundary}

    mime_type = mimetypes.guess_type(filename)[0]
    if mime_type is None:
        mime_type = 'application/octet-stream'

    body = b'--' + boundary.encode() + b'\r\n' + \
           b'Content-Disposition: form-data; name="upload_file"; filename="%s"\r\n' % filename.encode() + \
           b'Content-Type: %s\r\n\r\n' % mime_type.encode()

    with open(file_path, 'rb') as f:
        body += f.read() + b'\r\n'

    if instruction is not None:
        body += b'--' + boundary.encode() + b'\r\n' + \
                b'Content-Disposition: form-data; name="instruction"\r\n\r\n' + \
                instruction.encode() + b'\r\n'

    body += b'--' + boundary.encode() + b'--\r\n'

    conn.request("POST", path, body=body, headers=headers)
    response = conn.getresponse()
    if response.status == 200:
        return response.read().decode()
    else:
        error_message = f'Failed to send file. Status code: {response.status}, Response: {response.read().decode()}'
        raise ValueError(error_message)
