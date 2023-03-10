import discord
import os.path
import time

import engagement_checker
import keys

users = {}
if (os.path.isfile("user_list.py")):
    print("found users")
    import user_list
    users = user_list.users
else:
    print("didn't find users")

posts = []
if (os.path.isfile("post_list.py")):
    print("found posts")
    import post_list
    posts = post_list.posts
else:
    print("didn't find posts")

print(f"USERS: {users}")

# ADD MORE INFO ABOUT HOW TO USE
post_message_intro = '''If it's your first time here, send a link to your LinkedIn profile first. Then you can send a link to your post.\n
Leave a like on every post here before linking your own post\n
Current posts:\n'''

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


async def check_engagement(account):
    print(f"checking for {users[account]}")
    for post in posts:
        print(f"checking post {post}")
        result = engagement_checker.check_post(post['post'], users[account])
        if (result == False):
            return False
    return True


def add_post(post, user):
    print("Adding post")
    posts[user] = post


async def update_post_message():
    print("Updating post message")
    channel = client.get_channel(linkedin_channel)
    message = await channel.fetch_message(post_message)

    new_text = post_message_intro

    if len(posts) > 3:
        del posts[0]

    for post in posts:
        new_text += f" - <{post['post']}>\n"
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


async def set_status(text):
    print("setting status")
    channel = client.get_channel(linkedin_channel)
    message = await channel.fetch_message(status_message)
    new_text = f"Status: Busy :no_entry:\n{text}"
    await message.edit(content=new_text)


def is_user_in_post_list(user):
    for post in posts:
        if (post['user'] == user):
            return True
    return False


def save_posts_to_file():
    print("saving posts")
    file = open("post_list.py", "w")
    file.write(f"posts = {posts}")


def save_users_to_file():
    print("saving users")
    file = open("user_list.py", "w")
    file.write(f"users = {users}")


@client.event
async def on_message(message):
    global status_message
    global post_message, posts, users
    msgtxt = str(message.content)
    if message.author == client.user:
        if (msgtxt.find("Current posts") > -1):
            post_message = message.id
            await update_post_message()
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
            if (message.author.id in users):
                print("user is registered")
                if (is_user_in_post_list(message.author.id) == False or message.author == "191925539206987776"):
                    plain_link = msgtxt
                    author = message.author.id
                    await message.delete()
                    await set_status("Currently checking engagement on listed posts 🕵️")
                    passed_engagement_check = await check_engagement(author)
                    if (passed_engagement_check):
                        if (plain_link.find("?") > -1):
                            plain_link = cutendpos(msgtxt, msgtxt.find("?"))
                        posts.append({'user': author, 'post': plain_link})
                        print(f"POSTS: {posts}")
                        await update_post_message()
                        await status_update("Thank you for sharing your post, added to the list")
                        save_posts_to_file()
                    else:
                        await status_update("❌Couldn't find likes from you on all listed posts.❌")
                else:
                    print("already a post in list")
                    await message.delete()
                    await status_update("You already have a post in the list, please wait")
            else:
                print("user is not registered")
                await message.delete()
                await status_update("No LinkedIn profile saved for you, please send a link to your LinkedIn Profile")
        elif (msgtxt.find("www.linkedin.com/in/") > -1):

            print("probably a profile link")
            print(msgtxt)
            username = cutstart(msgtxt, msgtxt.find("/in/") + 4)
            print(username)
            username = cutendpos(username, username.find("/"))
            print(username)
            users[message.author.id] = username

            await message.delete()
            save_users_to_file()

            await status_update(f"Thank you for adding your LinkedIn profile, {message.author.mention}. You may now share your posts after liking & commenting on the current ones")

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


client.run(keys.discord)
