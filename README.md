# Subtitle-Transcribe-Trailer
Utilizing AWS Transcribe to showcase possible functionalities
***
### Three functionalities demonstrated in transcriber.py are: ###
1. Upload object to S3
2. Transcribe audio from MP4 files utilizing AWS Transcribe
3. Implement subtitles onto Avengers trailer using OpenCV with JSON single word Transcribe response as well as built in subtitle response from Transcribe and attach original audio back onto video
***
### Below is a list of functions that are included in the transcriber.py file: ###
* upload_s3_object - upload file to s3 bucket
* aws_start_transcription - start transcription of s3 file
* aws_get_transcription - get status and data of transcription already started
* convert_trailer_frames_to_transcribed_video - put subtitles on video utilizing exact word placement when said
* convert_trailer_frames_to_transcribed_video_vtt - put subtitles on video utilizing vtt format
* download_transcript - download transcript or any file and save locally
* convert_vtt_to_seconds - function to convert vtt time to seconds
***
### Below is a list of functions that are included in the helpers.py file: ###
* atoi/natural_keys - sort functions found on stack overflow to correctly organize frames
* turn_trailer_back_to_movie - stitch frames together to original mp4 format and now reattach audio
* turn_trailer_to_frames - turn trailer mp4 into individual jpg frames
