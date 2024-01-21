import http.client
import mimetypes
import os


def upload_file(file_path, *, dev=False):
    host = "localhost:5328" if dev else "ivette-py.vercel.app"
    conn = http.client.HTTPSConnection(
        host) if not dev else http.client.HTTPConnection(host)
    boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
    headers = {'Content-Type': 'multipart/form-data; boundary=' + boundary}
    with open(file_path, 'rb') as f:
        file_content = f.read()
    filename = os.path.basename(file_path)
    mimetype = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    data = []
    data.append('--' + boundary)
    data.append(
        f'Content-Disposition: form-data; name="file"; filename="{filename}"')
    data.append(f'Content-Type: {mimetype}')
    data.append('')
    data.append(file_content)
    data.append('--' + boundary + '--')
    data.append('')
    payload = b'\r\n'.join(
        d.encode() if isinstance(d, str) else d for d in data)
    conn.request("POST", "/api/python/upload_file",
                 body=payload, headers=headers)
    res = conn.getresponse()
    return res.read().decode("utf-8")


if __name__ == "__main__":
    print(upload_file('README.md'))