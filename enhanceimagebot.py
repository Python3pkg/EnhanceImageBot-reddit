#!/usr/bin/env python3.2

# =============================================================================
# IMPORTS
# =============================================================================

import requests
import requests.auth
import praw
import configparser
from pprint import pprint
import traceback
from urllib.request import urlopen, urlretrieve
from pgmagick import Geometry, Image
from imgurpython import ImgurClient
from prawoauth2 import PrawOAuth2Mini

# =============================================================================
# GLOBALS
# =============================================================================

# Reads the config file
config = configparser.ConfigParser()
config.read("EnhanceImageBot.cfg")

#Reddit info
user_agent = ("EnhanceImage v0.3 by /u/sprunth")
r = praw.Reddit(user_agent = user_agent)
CLIENT_ID = config.get("Reddit", "client_id")
CLIENT_SECRET = config.get("Reddit", "client_secret")
TOKEN = config.get('Reddit', 'token')
REFRESH_TOKEN = config.get('Reddit', 'refresh_token')
SCOPES = ['identity', 'submit']

imgur_client_id = config.get('Imgur', 'client_id')
imgur_client_secret = config.get('Imgur', 'client_secret')
imgur_access_token = config.get('Imgur', 'access_token')
imgur_refresh_token = config.get('Imgur', 'refresh_token')

imgur_client = ImgurClient(imgur_client_id, imgur_client_secret, imgur_access_token, imgur_refresh_token)

already_done = set()

oauth_helper = PrawOAuth2Mini(r, app_key=CLIENT_ID, app_secret=CLIENT_SECRET, access_token=TOKEN, refresh_token=REFRESH_TOKEN, scopes=SCOPES)

# =============================================================================
# FUNCTIONS
# =============================================================================

def getTopSubmissions():
    print("Ready for images")    
    subreddit = r.get_subreddit('test')
    for comment in praw.helpers.comment_stream(r, 'test', limit=10, verbosity=0):
        oauth_helper.refresh()
        comment_utf8 = comment.body.encode('utf-8')
        if comment_utf8.startswith(b'Enhance!'):
            
            pprint("New Image %s from %s" % (comment.submission.url, comment.permalink))
            
            destinationName = checkurl(comment.submission.url)
            if destinationName == None:
                continue

            # image is good, downloaded as destinationName
            processResult = enhanceImage(destinationName)

            if processResult == True:
                uploadedURL = uploadToImgur(comment, destinationName)
                pprint('enhanced image uploaded to %s' % uploadedURL)
                replyResult = replyToPost(comment, uploadedURL)
                print('Replied')

            # mark image as done regardless of whether it actually worked
            already_done.add(comment.id)
            print("Image Finished")

def checkurl(url):
    """Verify the url is good (is image)
    If so, downloads the image and returns the localpath to it"""

    extension = url.split('.')[-1].upper()
    if extension not in ['BMP', 'GIF', 'JPEG', 'JPG', 'PNG', 'TIF', 'TIFF']:
        return None

    try:
        info = urlopen(url).info()
        imagesize = int(info._headers[[i for i, v in enumerate(info._headers) if v[0] == 'Content-Length'][0]][1])

        pprint('image size: %s' % imagesize)

        # if over 1MB
        if imagesize/1024 > 1000:
            print('Image too large')
            return False

        destinationName = 'image.'+extension
        urlretrieve(url, destinationName)
        return destinationName

    except:
        return None

def enhanceImage(localpath):
    """Crop to 50%, and resize to original size
        sharpen, save out to same image name
        Returns True if image processing succeeds"""
    try:
        img = Image(localpath)
        
        size = img.size()
        geo = Geometry(round(size.width()*0.5), round(size.height()*0.5), round(size.width()*0.25), round(size.height()*0.25))
        img.crop(geo)
        img.scale(size)
        img.quality(80)
        img.sharpen(1)
        img.write(localpath)
        print(("Image written to %s" % localpath))
    except:
        return False

    return True

def uploadToImgur(comment, img_path):
    upload_config = dict()
    upload_config['title'] = 'Enhanced image for %s by /u/EnhanceImageBot' % comment.author
    upload_config['description'] = comment.permalink

    image = imgur_client.upload_from_path(img_path, upload_config)
    return image['link']

def replyToPost(comment, uploadedURL):
    while True:
        try:
            comment = comment.reply('[Enhanced Image!](%s)\n\n^See ^/r/EnhaceImageBot ^for ^more ^info' % uploadedURL)
            return comment
        except praw.errors.RateLimitExceeded as error:
            print(("RateLimitExceeded. Trying again in %s seconds" % error.sleep_time))
        except:
            print("Unknown error")
            break

# =============================================================================
# MAIN
# =============================================================================

def main(): 
    oauth_helper.refresh()
    try:
        authenticated_user = r.get_me()
        print(('Authenticated! Logged in as %s' % authenticated_user.name))
        getTopSubmissions()
    except Exception as e:
        print(('Error: ', e))
        print((traceback.format_exc()))
    finally:
        print('Closing')


# =============================================================================
# RUNNER
# =============================================================================

if __name__ == '__main__':
    main()

