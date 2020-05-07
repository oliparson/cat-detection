# cat-detection

This repository collects my attempts to train a machine learning algorithm to detect whether my cat is in the house using only camera images.

<img src="https://github.com/oliparson/cat-detection/blob/master/animation.gif" width="40%">

You can follow my progress on the [Non-intrusive Cat Monitoring blog](https://nonintrusivecatmonitoring.blogspot.com/).

The diagram below gives an overview of how the logic is spread across the Raspberry Pi and Google Cloud.
![Cat detection architecture diagram](https://github.com/oliparson/cat-detection/blob/master/cat_detection_architecture.png)

The script `upload_photo.sh`:
1. takes a photo and saves it to the `~/Pictures/` directory
2. uploads it to a Google Cloud Storage bucket
3. deletes the file from the `~/Pictures/` directory
