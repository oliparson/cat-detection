
while :
do
	DATE=$(date +"%Y-%m-%d_%H%M%S")
	FILENAME="/home/pi/Pictures/$DATE.jpg"

	# Take photo and save to Raspberry Pi SD card
	raspistill -o $FILENAME

	# Upload photo to Google Cloud Storage bucket
	curl -X POST --data-binary @$FILENAME \
	-H "Authorization: Bearer $OAUTH2_TOKEN" \
	-H "Content-Type: image/jpg" \
	"https://storage.googleapis.com/upload/storage/v1/b/catflap-photos-raw/o?uploadType=media&name=$DATE.jpy"

	# Remove photo from Raspberry Pi SD card
	rm $FILENAME
done
