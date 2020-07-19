
import datetime

from flask import Flask, render_template, request, abort
from google.auth.transport import requests
from google.cloud import storage
import google.oauth2.id_token
import pandas as pd
import numpy as np

app = Flask(__name__)

date_format = '%Y-%m-%d'

def get_cat_detection_list(date):

    # Get list of results objects
    model_bucket_name = 'cat-detection-models'
    client = storage.Client()
    model_bucket = client.bucket(model_bucket_name)
    blobs = model_bucket.list_blobs(prefix=f'batch-output-keys/{date}')
    blob_list = [blob.name for blob in blobs]
    result_list = [x for x in blob_list if 'results' in x]

    # Read results objects in single pandas DataFrame
    df_list = []
    for blob in blob_list:
        labels = pd.read_json('gs://'+model_bucket_name+'/'+blob, lines=True)
        df_list += [labels]
    prediction_df = pd.concat(df_list, ignore_index=True, sort=False)

    if len(prediction_df) == 0:
        return []

    # Get cat detections and create list of URLs
    prediction_df['prediction'] = prediction_df.babyweight.apply(np.argmax)
    detection_df = prediction_df[prediction_df.prediction==1]
    detection_df['gcs_path'] = f'https://storage.cloud.google.com/catflap-photos-raw/' + detection_df.key
    detection_list = detection_df.gcs_path.tolist()

    return detection_list

def authenticate_and_list(date):

    # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    detection_list = []
    prev_date = ''
    next_date = ''

    if id_token:
        try:
            # Verify the token against the Firebase Auth API. This example
            # verifies the token on each page load. For improved performance,
            # some applications may wish to cache results in an encrypted
            # session store (see for instance
            # http://flask.pocoo.org/docs/1.0/quickstart/#sessions).
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

            if claims['user_id'] == 'nxDIYN03mghB1RL6v7wp4ydPHMQ2':
                detection_list = get_cat_detection_list(date)

                pd_date = pd.Timestamp(date)
                prev_date = (pd_date - pd.Timedelta('1D')).strftime(format=date_format)
                next_date = (pd_date + pd.Timedelta('1D')).strftime(format=date_format)

        except ValueError as exc:
            # This will be raised if the token is expired or any other
            # verification checks fail.
            error_message = str(exc)

    return render_template('index.html',
                            blobs=detection_list,
                            prev_date=prev_date,
                            next_date=next_date)

firebase_request_adapter = requests.Request()

@app.route('/favicon.ico/')
def favicon():

    abort(404)

@app.route('/')
def root():

    date = pd.Timestamp.now().strftime(format=date_format)
    return authenticate_and_list(date)

@app.route('/<string:date>/')
def root_date(date):

    return authenticate_and_list(date)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
