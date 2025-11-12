import requests

class OBSClient:
    def __init__(self, access_key_id, access_key_secret, endpoint):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.endpoint = endpoint

    def connect(self):
        return requests.Session()

    def create_bucket(self, bucket_name):
        session = self.connect()
        url = f"{self.endpoint}/?bucket={bucket_name}"
        headers = {
            'Content-Type': 'application/json',
            'Date': 'Fri, 10 Jun 2022 11:00:00 GMT',
            'Authorization': f'AWS {self.access_key_id}:{self.access_key_secret}'
        }
        data = {
            'bucket': bucket_name
        }
        response = session.put(url, headers=headers, data=data)
        return response.status_code == 200

    def get_buckets(self):
        session = self.connect()
        url = f"{self.endpoint}/"
        headers = {
            'Content-Type': 'application/json',
            'Date': 'Fri, 10 Jun 2022 11:00:00 GMT',
            'Authorization': f'AWS {self.access_key_id}:{self.access_key_secret}'
        }
        response = session.get(url, headers=headers)
        return response.json()

    def delete_bucket(self, bucket_name):
        session = self.connect()
        url = f"{self.endpoint}/{bucket_name}"
        headers = {
            'Content-Type': 'application/json',
            'Date': 'Fri, 10 Jun 2022 11:00:00 GMT',
            'Authorization': f'AWS {self.access_key_id}:{self.access_key_secret}'
        }
        response = session.delete(url, headers=headers)
        return response.status_code == 204

    def upload_object(self, bucket_name, object_name, file_path):
        session = self.connect()
        url = f"{self.endpoint}/{bucket_name}/{object_name}"
        headers = {
            'Content-Type': 'application/octet-stream',
            'Date': 'Fri, 10 Jun 2022 11:00:00 GMT',
            'Authorization': f'AWS {self.access_key_id}:{self.access_key_secret}'
        }
        with open(file_path, 'rb') as file:
            response = session.put(url, headers=headers, data=file)
        return response.status_code == 200

    def get_object(self, bucket_name, object_name):
        session = self.connect()
        url = f"{self.endpoint}/{bucket_name}/{object_name}"
        headers = {
            'Content-Type': 'application/octet-stream',
            'Date': 'Fri, 10 Jun 2022 11:00:00 GMT',
            'Authorization': f'AWS {self.access_key_id}:{self.access_key_secret}'
        }
        response = session.get(url, headers=headers)
        return response.content

    def get_object_list(self, bucket_name):
        session = self.connect()
        url = f"{self.endpoint}/{bucket_name}?delimiter=/&prefix="
        headers = {
            'Content-Type': 'application/json',
            'Date': 'Fri, 10 Jun 2022 11:00:00 GMT',
            'Authorization': f'AWS {self.access_key_id}:{self.access_key_secret}'
        }
        response = session.get(url, headers=headers)
        return response.json()

    def delete_object(self, bucket_name, object_name):
        session = self.connect()
        url = f"{self.endpoint}/{bucket_name}/{object_name}"
        headers = {
            'Content-Type': 'application/json',
            'Date': 'Fri, 10 Jun 2022 11:00:00 GMT',
            'Authorization': f'AWS {self.access_key_id}:{self.access_key_secret}'
        }
        response = session.delete(url, headers=headers)
        return response.status_code == 204

    def rename_object(self, bucket_name, old_object_name, new_object_name):
        session = self.connect()
        url = f"{self.endpoint}/{bucket_name}/{old_object_name}"
        headers = {
            'Content-Type': 'application/json',
            'Date': 'Fri, 10 Jun 2022 11:00:00 GMT',
            'Authorization': f'AWS {self.access_key_id}:{self.access_key_secret}'
        }
        data = {
            'copySource': f"{bucket_name}/{old_object_name}",
            'x-obs-copy-source': f"{self.endpoint}/{bucket_name}/{old_object_name}",
            'x-amz-copy-object-id': new_object_name
        }
        response = session.put(url, headers=headers, data=data)
        return response.status_code == 200

    def copy_object(self, bucket_name, source_object_name, destination_object_name):
        session = self.connect()
        url = f"{self.endpoint}/{bucket_name}/{destination_object_name}"
        headers = {
            'Content-Type': 'application/json',
            'Date': 'Fri, 10 Jun 2022 11:00:00 GMT',
            'Authorization': f'AWS {self.access_key_id}:{self.access_key_secret}'
        }
        data = {
            'copySource': f"{bucket_name}/{source_object_name}",
            'x-obs-copy-source': f"{self.endpoint}/{bucket_name}/{source_object_name}"
        }
        response = session.put(url, headers=headers, data=data)
        return response.status_code == 200

    def move_object(self, bucket_name, source_object_name, destination_object_name):
        session = self.connect()
        url = f"{self.endpoint}/{bucket_name}/{source_object_name}"
        headers = {
            'Content-Type': 'application/json',
            'Date': 'Fri, 10 Jun 2022 11:00:00 GMT',
            'Authorization': f'AWS {self.access_key_id}:{self.access_key_secret}'
        }
        data = {
            'copySource': f"{bucket_name}/{source_object_name}",
            'x-obs-copy-source': f"{self.endpoint}/{bucket_name}/{source_object_name}",
            'x-amz-copy-object-id': destination_object_name
        }
        response = session.put(url, headers=headers, data=data)
        return response.status_code == 200

    def download_object(self, bucket_name, object_name, file_path):
        session = self.connect()
        url = f"{self.endpoint}/{bucket_name}/{object_name}"
        headers = {
            'Content-Type': 'application/octet-stream',
            'Date': 'Fri, 10 Jun 2022 11:00:00 GMT',
            'Authorization': f'AWS {self.access_key_id}:{self.access_key_secret}'
        }
        response = session.get(url, headers=headers)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return response.status_code == 200

