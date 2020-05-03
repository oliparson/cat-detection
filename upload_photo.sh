DATE=$(date +"%Y-%m-%d_%H%M%S")
FILENAME="/home/pi/Pictures/$DATE.jpg"

raspistill -o $FILENAME

curl -X POST --data-binary @$FILENAME \
-H "Authorization: Bearer $OAUTH2_TOKEN" \
-H "Content-Type: image/jpg" \
"https://storage.googleapis.com/upload/storage/v1/b/catflap-photos-raw/o?uploadType=media&name=$DATE.jpy"
