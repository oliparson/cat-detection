
while :
do
	DATE=$(date +"%Y-%m-%d_%H%M%S")
	FILENAME="/home/pi/Pictures/$DATE.jpg"

	# Take photo and save to Raspberry Pi SD card
	raspistill -rot 180 -w 800 -h 600 -o $FILENAME

	# Upload photo to Google Cloud Storage bucket
	response=$(curl --silent --show-error -X POST --data-binary @$FILENAME \
	-H "Authorization: Bearer $OAUTH2_TOKEN" \
	-H "Content-Type: image/jpg" \
	"https://storage.googleapis.com/upload/storage/v1/b/catflap-photos-raw/o?uploadType=media&name=$DATE.jpg")
	
	# Remove photo from Raspberry Pi SD card
	rm $FILENAME

	# Quit after 8pm
	hour=$(date +"%-H")
	if (( $hour > 19 ))
	then
		echo end of log
		exit 1
	fi
	
	# Recreate auth code if it's expired
	error_code=$(echo $response | jq -r '.error.code')
	echo $DATE $error_code
	if [ "$error_code" = "401" ]
	then
		echo Renewing gcloud oauth token
		OAUTH2_TOKEN=$(gcloud auth print-access-token)
	fi

done
