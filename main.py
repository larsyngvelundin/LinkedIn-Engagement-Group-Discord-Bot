import discord
import sqlite3
import os.path
import time

import keys

# check for saved users and load them in
posts = {}
users = {}

if (os.path.isfile("users.py")):
    print("found users")
else:
    print("didn't find users")

if (os.path.isfile("posts.py")):
    print("found posts")
else:
    print("didn't find posts")

post_message_intro = "Leave a like and a comment on every post here before linking your own post\nCurrent posts:\n"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
linkedin_channel = ""

post_message = ""
status_message = ""
max_posts = 10


def cutstart(s, n):  # Cuts n amount of characters from string
    return s[n:]


def cutend(s, n):  # Cuts end of string n = characters from end
    end = len(s) - n
    return s[0:end]


def cutendpos(s, n):  # Cuts end of a string n = characters from start
    return s[0:n]


def check_engagement(account):
    print("checking")


def add_post(post, user):
    print("Adding post")
    posts[user] = post


async def update_post_message():
    print("Updating post message")
    channel = client.get_channel(linkedin_channel)
    message = await channel.fetch_message(post_message)

    new_text = post_message_intro
    for user in posts:
        new_text += f" - <{posts[user]}>"
    await message.edit(content=new_text)


async def status_update(text):
    print("updating status")
    channel = client.get_channel(linkedin_channel)
    message = await channel.fetch_message(status_message)
    new_text = f"Status: Busy :no_entry:\n{text}"
    await message.edit(content=new_text)

    time.sleep(7)
    new_text = "Status: Available :white_check_mark:"
    await message.edit(content=new_text)


# [
# {user: 011001001, post: "https:linkedin.com/post/123490124"}
# {user: 011001001, post: "https:linkedin.com/post/123490124"}
# ]

# can append to end
# can pop oldest


@client.event
async def on_message(message):
    global status_message
    global post_message, posts, users
    msgtxt = str(message.content)
    if message.author == client.user:
        if (msgtxt.find("Current posts") > -1):
            post_message = message.id
        if (msgtxt.find("Status:") > -1):
            status_message = message.id
        return

    if (message.channel.id == linkedin_channel):
        print(f"my status_message is {status_message}")
        print(f"my post_message is {post_message}")
        print("we in linkedin channel")
        print(msgtxt.find("http"))
        if (msgtxt.find('www.linkedin.com/posts/') > -1):
            print("probably a post link")

            # check if user had saved their linkedin username
            # if saved,
            if (message.author in users):
                print("user is registered")
                # check current posts to see if they commented and liked
                # if yes,
                # add their link to list (remove last if over limit)
                if (message.author not in posts):
                    plain_link = msgtxt
                    if (plain_link.find("?") > -1):
                        plain_link = cutendpos(msgtxt, msgtxt.find("?"))
                    posts[message.author] = plain_link
                    await message.delete()
                    await update_post_message()
                    await status_update("Thank you for sharing your post, added to the list")
                else:
                    print("already a post in list")
                    await message.delete()
                    await status_update("You already have a post in the list, please wait")
            # if no
            else:
                print("user is not registered")
                await status_update("No LinkedIn profile saved for you, please send a link to your LinkedIn Profile")
                await message.delete()
                # status message says check failed.
        elif (msgtxt.find("www.linkedin.com/in/") > -1):

            print("probably a profile link")
            print(msgtxt)
            username = cutstart(msgtxt, msgtxt.find("/in/") + 4)
            print(username)
            username = cutendpos(username, username.find("/"))
            print(username)
            users[message.author] = username

            await message.delete()

            await status_update(f"Thank you for adding your LinkedIn profile, {message.author.mention}")

        #
        else:
            print("ONLY LINKS ALLOWED, PURGE")
            await message.delete()

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    for chan in client.get_all_channels():
        if (str(chan.name) == "linkedin-posts"):
            global linkedin_channel
            linkedin_channel = chan.id
    if (linkedin_channel == ""):
        print("LinkedIn Channel not found, exiting")
        exit()
    else:
        print("found")
        channel = client.get_channel(linkedin_channel)
        async for message in channel.history(limit=200):
            await message.delete()

        await channel.send(post_message_intro)

        await channel.send("Status: Available :white_check_mark:")

        # get all message, remove non-bot
        # check if 2 messages exist from bot
        # if not, send 2 messages
        # if do, save message IDs for editing later

client.run(keys.discord)

# https://www.linkedin.com/posts/sakerhetspolisen_saeukerhetspolisen2022abr2023-activity-7034825294343483393-YATY?utm_source=share&utm_medium=member_desktop
