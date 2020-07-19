
import datetime

from flask import Flask, render_template
from google.cloud import storage
import pandas as pd
import numpy as np

app = Flask(__name__)


@app.route('/')
def root():

    # Get list of results objects
    model_bucket_name = 'cat-detection-models'
    client = storage.Client()
    model_bucket = client.bucket(model_bucket_name)
    blobs = model_bucket.list_blobs(prefix=f'batch-output-keys/2020-07-19_11')
    blob_list = [blob.name for blob in blobs]
    result_list = [x for x in blob_list if 'results' in x]

    # Read results objects in single pandas DataFrame
    df_list = []
    for blob in blob_list:
        labels = pd.read_json('gs://'+model_bucket_name+'/'+blob, lines=True)
        df_list += [labels]
    prediction_df = pd.concat(df_list, ignore_index=True, sort=False)

    # Get cat detections and create list of URLs
    prediction_df['prediction'] = prediction_df.babyweight.apply(np.argmax)
    detection_df = prediction_df[prediction_df.prediction==1]
    detection_df['gcs_path'] = f'https://storage.cloud.google.com/catflap-photos-raw/' + detection_df.key
    detection_list = detection_df.gcs_path.tolist()

    return render_template('index.html', times=detection_list)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
