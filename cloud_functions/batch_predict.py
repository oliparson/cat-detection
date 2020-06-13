
import io
import json
import time
import re
from google.cloud import storage
from googleapiclient import discovery, errors
import matplotlib.image as mpimg
import pandas as pd

def make_batch_job_body(project_name, input_paths, output_path,
            model_name, region, data_format='JSON',
            version_name=None, max_worker_count=None,
            runtime_version=None):

    project_id = 'projects/{}'.format(project_name)
    model_id = '{}/models/{}'.format(project_id, model_name)
    if version_name:
        version_id = '{}/versions/{}'.format(model_id, version_name)

    # Make a jobName of the format "model_name_batch_predict_YYYYMMDD_HHMMSS"
    timestamp = time.strftime('%Y%m%d_%H%M%S', time.gmtime())

    # Make sure the project name is formatted correctly to work as the basis
    # of a valid job name.
    clean_project_name = re.sub(r'\W+', '_', project_name)

    job_id = '{}_{}_{}'.format(clean_project_name, model_name,
                               timestamp)

    # Start building the request dictionary with required information.
    body = {'jobId': job_id,
            'predictionInput': {
                'dataFormat': data_format,
                'inputPaths': input_paths,
                'outputPath': output_path,
                'region': region}}

    # Use the version if present, the model (its default version) if not.
    if version_name:
        body['predictionInput']['versionName'] = version_id
    else:
        body['predictionInput']['modelName'] = model_id

    # Only include a maximum number of workers or a runtime version if specified.
    # Otherwise let the service use its defaults.
    if max_worker_count:
        body['predictionInput']['maxWorkerCount'] = max_worker_count

    if runtime_version:
        body['predictionInput']['runtimeVersion'] = runtime_version

    return body

def hello_world(request):


    # Define bucket and blob prefix
    project = 'optimum-treat-262616'
    photo_bucket_name = 'catflap-photos-raw'
    model_bucket_name = 'cat-detection-models'
    
    now = pd.Timestamp.now(tz='Europe/London')
    previous_hour = now - pd.Timedelta(hours=1)
    prefix = previous_hour.strftime('%Y-%m-%d_%H')

    # Set up buckets
    client = storage.Client()
    photo_bucket = client.get_bucket(photo_bucket_name)
    model_bucket = client.get_bucket(model_bucket_name)

    # Get list of blob names
    blobs = photo_bucket.list_blobs(prefix=prefix)
    blob_list = [blob.name for blob in blobs]
    print(len(blob_list))
    
    # Read labels into pandas dataframe
    batch_input_filename = f'batch-input-{prefix}.json'
    fp = io.StringIO()
    for idx, blob_name in enumerate(blob_list[:]):
        # Read blob from GCS
        blob = photo_bucket.blob(blob_name)
        blob_str = blob.download_as_string()
        bytes_io = io.BytesIO(blob_str)
        img = mpimg.imread(bytes_io, format='jpg')
        img_red_downsample = img[::10,::10,0]
        # Write to file
        json_instances_dict = {'flatten_input': img_red_downsample.tolist(), 'key': blob_name}
        json.dump(json_instances_dict, fp)
        fp.write('\n')
        # Print progress
        if idx % 100 == 0:
            print(idx)
    fp.seek(0)

    # Upload batch input json file to GCS
    batch_input_blob = model_bucket.blob('batch-input-keys/'+prefix+'.json')
    batch_input_blob.upload_from_file(fp)

    # Create batch job body
    batch_predict_body = make_batch_job_body(
        project_name = project, 
        input_paths = f'gs://{model_bucket_name}/batch-input-keys/{prefix}.json', 
        output_path = f'gs://{model_bucket_name}/batch-output-keys/{prefix}/',
        model_name = 'logistic_regression_v2', 
        region = 'europe-west2',
        version_name='logistic_regression_v2', 
        max_worker_count=20)

    # Submit batch prediction job
    project_id = 'projects/{}'.format(project)
    ml = discovery.build('ml', 'v1')
    request = ml.projects().jobs().create(parent=project_id, body=batch_predict_body)
    try:
        response = request.execute()
        print('Job requested.')
        # The state returned will almost always be QUEUED.
        print('state : {}'.format(response['state']))
        return 'Job requested.'
    except errors.HttpError as err:
        # Something went wrong, print out some information.
        print('There was an error getting the prediction results.' +
              'Check the details:')
        print(err._get_reason())
        return 'Job error.'
