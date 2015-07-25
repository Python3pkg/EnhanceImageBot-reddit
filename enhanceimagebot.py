#!/usr/bin/env python3.2

# =============================================================================
# IMPORTS
# =============================================================================

import requests
import requests.auth
import praw
import OAuth2Util
import configparser

# =============================================================================
# GLOBALS
# =============================================================================

# Reads the config file
config = configparser.ConfigParser()
config.read("EnhanceImageBot.cfg")

#Reddit info
user_agent = ("EnhanceImageBot v0.1 by /u/sprunth")
r = praw.Reddit(user_agent = user_agent)
CLIENT_ID = config.get("Reddit", "client_id")
CLIENT_SECRET = config.get("Reddit", "client_secret")
REDIRECT_URI = config.get("Reddit", "redirect_uri")

USERNAME = config.get("Reddit", "username")
PASSWORD = config.get("Reddit", "password")

# =============================================================================
# FUNCTIONS
# =============================================================================

# =============================================================================
# MAIN
# =============================================================================

def main():
    o = OAuth2Util.OAuth2Util(r);
    o.refresh();
    print('OAuth2 done')
    try:
        authenticated_user = r.get_me()
        print('Authenticated! ', authenticated_user.name, authenticated_user.link_karma)
    except:
        pass
    finally:
        print('Error')


# =============================================================================
# RUNNER
# =============================================================================

if __name__ == '__main__':
    r = praw.Reddit("EnhanceImage v0.1 by /u/sprunth")
    o = OAuth2Util.OAuth2Util(r, print_log=True)

    o.refresh()

    print("Hi, {0}, you have {1} comment karma!".format(
    r.get_me().name, r.get_me().comment_karma))


