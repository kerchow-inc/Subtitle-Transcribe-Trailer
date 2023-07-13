
import cv2
import glob
import re
import moviepy.editor as mp

# sort function found at https://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split(r'(\d+)', text)]


# altered function from video 1
# convert all frames with celebrity photos and names back into the original trailer
'''
    location(string): local folder where image frames are stored
    name(string): what output video will be called *including format ex. .mp4
    original(string): location of original video so that it can be used to restitch audio onto trailer *including format ex. .mp4
'''


def turn_trailer_back_to_movie(location, name, original):

    # get all trailer files
    trailer_frames = glob.glob(f"{location}//*")
    # get the height and width of one frame to initialize VideoWriter
    frames = cv2.imread(trailer_frames[0])
    height, width, layers = frames.shape

    video = cv2.VideoWriter(name, 0, 24, (width, height))

    # with glob it will not come out exactly in order ex. frames1,frames100,frames101
    # so this sorting functionality will put frame in order ex. frames1, frames2, frames3
    sort_frames = []
    for f in trailer_frames:
        sort_frames.append(f.replace('.jpg', '').replace(f'{location}\\', ''))
    sort_frames.sort(key=natural_keys)

    # stitch all frames back together
    for frame in sort_frames:
        video.write(cv2.imread(f'{location}//'+frame+'.jpg'))

    # close cv
    cv2.destroyAllWindows()
    video.release()

    # restitch audio onto trailer
    if original:
        new_video = mp.VideoFileClip(name)
        original_video = mp.AudioFileClip(original)
        final_clip = new_video.set_audio(original_video)
        final_clip.write_videofile(
            f"{name}".replace('.mp4', '_audio.mp4'))



# turn trailer to frames
'''
    trailer(string): location of trailer
    path_to_save(string): folder location to save frames
'''


def turn_trailer_to_frames(trailer, path_to_save):
    cap = cv2.VideoCapture(trailer)

    if (cap.isOpened() == False):
        return {}
    total_frame = 1

    # cap opened successfully
    while (cap.isOpened()):

        # capture each frame
        ret, frame = cap.read()
        if (ret == True):
            # Save frame as a jpg file
            name = 'frame' + str(total_frame) + '.jpg'
            cv2.imwrite(os.path.join(path_to_save, name), frame)

            total_frame += 1

        else:
            break
    # release capture
    cap.release()
