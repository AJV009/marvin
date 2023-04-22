import os
import re
import json
import requests
import io
from google.cloud import vision
from google.cloud import storage
from mimetypes import guess_type

class OCRHelper:
    def __init__(self, bucket_name='marvin-slack-bot-bucket'):
        self.bucket_name = bucket_name
        self.vision_client = vision.ImageAnnotatorClient()
        self.storage_client = storage.Client()

    def detect_text_uri(self, uri, is_url=False):
        if is_url:
            image = vision.Image()
            image.source.image_uri = uri
        else:
            with io.open(uri, 'rb') as image_file:
                content = image_file.read()
            image = vision.Image(content=content)
        response = self.vision_client.text_detection(image=image)
        texts = response.text_annotations

        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))

        return texts[0].description

    def async_detect_document(self, gcs_source_uri, gcs_destination_uri):
        mime_type = 'application/pdf'
        batch_size = 2

        feature = vision.Feature(
            type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

        gcs_source = vision.GcsSource(uri=gcs_source_uri)
        input_config = vision.InputConfig(
            gcs_source=gcs_source, mime_type=mime_type)

        gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
        output_config = vision.OutputConfig(
            gcs_destination=gcs_destination, batch_size=batch_size)

        async_request = vision.AsyncAnnotateFileRequest(
            features=[feature], input_config=input_config,
            output_config=output_config)

        operation = self.vision_client.async_batch_annotate_files(
            requests=[async_request])
        operation.result(timeout=420)

        match = re.match(r'gs://([^/]+)/(.+)', gcs_destination_uri)
        bucket_name = match.group(1)
        prefix = match.group(2)

        bucket = self.storage_client.get_bucket(bucket_name)
        blob_list = [blob for blob in list(bucket.list_blobs(
            prefix=prefix)) if not blob.name.endswith('/')]

        # output = blob_list[0]
        # json_string = output.download_as_string()
        # response = json.loads(json_string)
        response = []
        for blob in blob_list:
            json_string = blob.download_as_string()
            response.append(json.loads(json_string))

        return response

    def upload_to_gcs_and_detect_text(self, input_file, is_url=False, gcs_destination_uri=None):
        bucket = self.storage_client.get_bucket(self.bucket_name)

        if is_url:
            response = requests.get(input_file)
            response.raise_for_status()
            file_name = input_file.split("/")[-1]
            file_content = response.content
        else:
            with open(input_file, 'rb') as f:
                file_name = os.path.basename(input_file)
                file_content = f.read()

        blob = bucket.blob(file_name)
        blob.upload_from_string(file_content, content_type='application/pdf')

        gcs_source_uri = f'gs://{self.bucket_name}/{file_name}'

        if gcs_destination_uri is None:
            gcs_destination_uri = f'gs://{self.bucket_name}/output/'

        return self.async_detect_document(gcs_source_uri, gcs_destination_uri)

    def process(self, input_path, is_url=False):
        mime_type, encoding = guess_type(input_path)

        if mime_type == 'application/pdf':
            responses = self.upload_to_gcs_and_detect_text(input_path, is_url)
            pages = []
            # for page_response in response['responses']:
            #     annotation = page_response['fullTextAnnotation']
            #     pages.append(annotation['text'])
            for response in responses:
                for page_response in response['responses']:
                    annotation = page_response['fullTextAnnotation']
                    pages.append(annotation['text'])
            return pages

        elif mime_type in ['image/jpeg', 'image/png']:
            return self.detect_text_uri(input_path, is_url)
            # if is_url:
            #     return self.detect_text_uri(input_path)
            # else:
            #     with open(input_path, 'rb') as f:
            #         img_data = f.read()
            #     img_base64 = base64.b64encode(img_data).decode('UTF-8')
            #     uri = f"data:{mime_type};base64,{img_base64}"
            #     return self.detect_text_uri(uri)

        else:
            raise ValueError("Unsupported file type. Supported types are PDF, JPEG, and PNG.")

def write_object_to_file(obj, filename):
    with open(filename, 'w') as f:
        if isinstance(obj, str):
            f.write(obj + '\n')
        elif isinstance(obj, list):
            obj_str = '\n'.join([str(item) for item in obj])
            f.write(obj_str + '\n')
        else:
            obj_str = str(obj)
            f.write(obj_str + '\n')

# # Example usage:
# ocr_helper = OCRHelper()

# # For local PDF file
# result = ocr_helper.process('21583473018.pdf')
# write_object_to_file(result, 'output_5.txt')

# # For a PDF URL
# result = ocr_helper.process('https://www.sldttc.org/allpdf/21583473018.pdf', is_url=True)
# write_object_to_file(result, 'output_6.txt')

# # For local image file
# result = ocr_helper.process('hswv9Xi.png')
# write_object_to_file(result, 'output_7.txt')

# # For an image URL
# result = ocr_helper.process('https://i.imgur.com/hswv9Xi.png', is_url=True)
# write_object_to_file(result, 'output_8.txt')

