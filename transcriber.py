import boto3
import cv2
from dotenv import load_dotenv
import json
import os
import time
import urllib.request
import webvtt


import helpers

load_dotenv()

# load key and secret from local .env file
aws_access_key_id = os.getenv('key')
aws_secret_access_key = os.getenv('secret')

# initialize aws credentials with boto3
transcribe_client = boto3.client("transcribe", aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key, region_name="us-east-2")

s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key, region_name="us-east-2")


# upload object to s3 bucket
'''
    file_location(string): local file location that will be uploaded to s3
    s3_name(string): file name that it will be saved as in s3
'''


def upload_s3_object(file_location, s3_name):
    s3_directory = 'awstranscribes3example'
    with open(file_location, "rb") as f:
        s3_client.upload_fileobj(f, s3_directory, s3_name)

    # this is the key to the object
    return s3_directory + '/' + s3_name


# start transcription function
'''
    name(string): name we want our transcription job name to be
    key(string): location in s3 where media is stored
    format(string): format transcription will be handling
'''


def aws_start_transcription(name, key, format):
    transcription = transcribe_client.start_transcription_job(**{
        'TranscriptionJobName': name,
        'Media': {'MediaFileUri': key},
        'MediaFormat': format,
        'LanguageCode': 'en-US',
        'OutputBucketName': 'kerchow-content',
        'Subtitles': {
            'Formats': [
                'vtt',
            ],
            'OutputStartIndex': 1
        },
    })
    return transcription['TranscriptionJob']


# get transcription function status
'''
    name(string): name of transcription job to get status
'''


def aws_get_transcription(name):
    transcription = transcribe_client.get_transcription_job(**{
        'TranscriptionJobName': name,
    })
    return transcription['TranscriptionJob']


# converting trailer frames to transcribed video with audio
'''
    trailer(string): location of local video
'''


def convert_trailer_frames_to_transcribed_video(trailer):
    cap = cv2.VideoCapture(trailer)

    # load our transcript data
    j = open('transcript.json')
    transcript = json.load(j)

    if (cap.isOpened() == False):
        return {}

    # count the number of frames and fps
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = round(cap.get(cv2.CAP_PROP_FPS))
    cap.release()

    for i in range(int(frames)):
        # dividing the curr_frame by fps to get current time in seconds
        curr_second = i/(fps)
        save_file_name = 'trailer//frame'+str(i+1)+'.jpg'
        # read our current frame in
        photo = cv2.imread(save_file_name)

        # check to see if there is any results within our bounds
        for item in transcript['results']['items']:
            # make sure that it has data because some may not have any text
            if 'start_time' in item:
                start_time = item['start_time']
                end_time = item['end_time']
                word = item['alternatives'][0]['content']
                # see if our word is within our time frame
                if float(start_time) <= curr_second <= float(end_time):
                    # put the text onto the screen
                    cv2.putText(photo, word, (600, 600),
                                cv2.FONT_HERSHEY_COMPLEX, 2, (255, 255, 255), 2)
        # write our new file out
        cv2.imwrite(save_file_name.replace('trailer', 'transcript'), photo)
    # create the movie with audio
    helpers.turn_trailer_back_to_movie(
        'transcript', 'avengers_transcript.mp4', 'photos//avengers.mp4')


# converting trailer frames to transcribed video with audio
'''
    trailer(string): location of local video
    file_name(string): location of vtt file
'''


def convert_trailer_frames_to_transcribed_video_vtt(trailer, file_name):
    cap = cv2.VideoCapture(trailer)

    if (cap.isOpened() == False):
        return {}

    # count the number of frames and fps
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = round(cap.get(cv2.CAP_PROP_FPS))
    cap.release()

    for i in range(int(frames)):
        # dividing the curr_frame by fps to get current time in seconds
        curr_second = i/(fps)
        save_file_name = 'trailer//frame'+str(i+1)+'.jpg'
        # read our current frame in
        photo = cv2.imread(save_file_name)

        # check to see if there is any results within our bounds
        for caption in webvtt.read(file_name):
            # make sure that it has data because some may not have any text
            start_time = convert_vtt_to_seconds(caption.start)
            end_time = convert_vtt_to_seconds(caption.end)
            word = caption.text
            # see if our word is within our time frame
            if float(start_time) <= curr_second <= float(end_time):
                # put the text onto the screen
                cv2.putText(photo, word, (600, 600),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
        # write our new file out
        cv2.imwrite(save_file_name.replace('trailer', 'subtitles'), photo)
    # create the movie with audio
    helpers.turn_trailer_back_to_movie(
        'subtitles', 'avengers_subtitles.mp4', 'photos//avengers.mp4')


# download transcript to local json file
'''
    uri(string): location of our transcribed file
'''


def download_transcript(uri, file_name):
    urllib.request.urlretrieve(uri, file_name)


# convert vtt timestamp to seconds in float
'''
    curr(string): vtt timestamp
'''


def convert_vtt_to_seconds(curr):
    time_list = curr.split(':')
    reverse_time_list = time_list[::-1]
    # return seconds + minutes * 60 + hours * 3600
    return float(reverse_time_list[0]) + (float(reverse_time_list[1])*60) + (float(reverse_time_list[2])*3600)

# main function


def main():

    # avengers trailer transcription
    transcription_name = 'avengers3'
    original_video = 'photos//avengers.mp4'
    upload_s3_object(original_video, 'avengers.mp4')
    aws_start_transcription(
        transcription_name, 's3://kerchow-content/avengers.mp4', 'mp4')
    time.sleep(180)
    transcript_status = 'running'

    job = {}
    sub = None
    while transcript_status != 'COMPLETED':
        job = aws_get_transcription(transcription_name)
        if 'Subtitles' in job:
            sub = job['Subtitles']['SubtitleFileUris'][0]
        transcript_status = job['TranscriptionJobStatus']

        time.sleep(60)

    download_transcript(
        job['Transcript']['TranscriptFileUri'], "transcript.json")
    if sub is not None:
        download_transcript(sub, 'subtitles.vtt')
    # # once job is complete and we have our transcription
    # # we will put the subtitles onto the video
    # # using opencv and put audio back onto the new mp4 file
    convert_trailer_frames_to_transcribed_video(original_video)
    convert_trailer_frames_to_transcribed_video_vtt(
        original_video, 'subtitles.vtt')


if __name__ == "__main__":
    main()
