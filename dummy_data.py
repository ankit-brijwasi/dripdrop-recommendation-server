import datetime
import os
import random
import shutil
import threading
import uuid

from appwrite.id import ID
from appwrite.input_file import InputFile
import requests

from conf import settings
from conf import appwrite_conf


def add_users_and_posts():
    def create_posts(temp_location, i, user, j, liked_by):
        print(f"adding post {j} for user {i}")
        response = requests.get(
            url="https://picsum.photos/id/{}/600/600".format(random.randint(0, 1084)),
            stream=True
        )

        # save file to a temp location
        if response.status_code == 200:
            path = f"{temp_location}/{uuid.uuid4()}.jpeg"
            with open(path, 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)

            # upload a file to storage
            file = appwrite_conf.storages.create_file(
                settings.APPWRITE_USER_DATA_STORAGE_ID,
                ID.unique(),
                InputFile.from_path(path)
            )

            post_data = {
                "posted_on": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "user_id": user.get("$id"),
                "caption": f"Parent Iteration: {i} and Loop Iteration: {j}",
                "file_ids": [file.get("$id")]
            }

            if(random.randint(0, 1) == 1):
                if len(liked_by) > 1:
                    n = random.randint(0, (len(liked_by) - 1))
                    post_data["liked_by"] = random.choices(liked_by, k=n)
                else:
                    post_data["liked_by"] = liked_by

            # create post
            appwrite_conf.databases.create_document(
                settings.APPWRITE_DATABASE_ID,
                settings.APPWRITE_POST_COLLECTION,
                ID.unique(),
                post_data
            )

            # remove file from temp location
            os.remove(path)
            print(f"added post {j} for user {i}")
        else:
            print("skip")

    def create_user_and_profiles(temp_location, user_ids, i):
        # create user account
        print(f"adding user: {i}")
        user = appwrite_conf.users.create(
            ID.unique(),
            f'user{i}@dripdrop.com',
            password='TestUser123',
            name=f"Test User {i}"
        )

        # create user profile
        print(f"adding user profile: {i}")
        appwrite_conf.databases.create_document(
                settings.APPWRITE_DATABASE_ID,
                settings.APPWRITE_PROFILE_COLLECTION,
                ID.unique(),
                {
                    "username": f"testuser.{i}",
                    "user_id": user.get("$id")
                }
            )

        if(random.randint(0, 1)): user_ids.append(user.get("$id"))
        threads = []

        # create posts
        for j in range(1, random.randint(10, 51)):
            threads.append(
                    threading.Thread(
                        target=create_posts,
                        args=(temp_location, i, user, j, user_ids)
                    )
                )

        for thread in threads: thread.start()
        for thread in threads: thread.join()

    temp_location = settings.BASE_DIR / "temp"
    temp_location.mkdir(exist_ok=True, parents=True)
    user_ids = []

    threads = [
        threading.Thread(
            target=create_user_and_profiles,
            args=(temp_location, user_ids, i)
        ) for i in range(1, 21)
    ]

    for thread in threads: thread.start()
    for thread in threads: thread.join()


def remove_users_and_posts():
    def remove_users():
        users = appwrite_conf.users.list()
        total = users.get("total")

        print("Removing all the users...")
        while total != 0:
            for user in users.get("users"):
                appwrite_conf.users.delete(user.get("$id"))

            users = appwrite_conf.users.list()
            total = users.get("total")
    
    def remove_profiles():
        profiles = appwrite_conf.databases.list_documents(
            settings.APPWRITE_DATABASE_ID,
            settings.APPWRITE_PROFILE_COLLECTION
        )
        total = profiles.get("total")

        print("Removing all the profiles...")
        while total != 0:
            for profile in profiles.get("documents"):
                appwrite_conf.databases.delete_document(
                    settings.APPWRITE_DATABASE_ID,
                    settings.APPWRITE_PROFILE_COLLECTION,
                    profile.get("$id")
                )

            profiles = appwrite_conf.databases.list_documents(
                settings.APPWRITE_DATABASE_ID,
                settings.APPWRITE_PROFILE_COLLECTION
            )
            total = profiles.get("total")
            
    def remove_posts():
        posts = appwrite_conf.databases.list_documents(
            settings.APPWRITE_DATABASE_ID,
            settings.APPWRITE_POST_COLLECTION
        )
        total = posts.get("total")

        print("Removing all the posts...")
        while total != 0:
            for post in posts.get("documents"):
                appwrite_conf.databases.delete_document(
                    settings.APPWRITE_DATABASE_ID,
                    settings.APPWRITE_POST_COLLECTION,
                    post.get("$id")
                )

            posts = appwrite_conf.databases.list_documents(
                settings.APPWRITE_DATABASE_ID,
                settings.APPWRITE_POST_COLLECTION
            )
            total = posts.get("total")

    def remove_files():
        files = appwrite_conf.storages.list_files(
            settings.APPWRITE_USER_DATA_STORAGE_ID
        )
        total = files.get("total")

        print("Removing all the files...")
        while total != 0:
            for file in files.get("files"):
                appwrite_conf.storages.delete_file(
                    settings.APPWRITE_USER_DATA_STORAGE_ID,
                    file.get("$id")
                )

            files = appwrite_conf.storages.list_files(settings.APPWRITE_USER_DATA_STORAGE_ID)
            total = files.get("total")

    threads = [
        threading.Thread(target=func) \
        for func in [remove_users, remove_profiles, remove_posts, remove_files]
    ]

    for thread in threads: thread.start()
    for thread in threads: thread.join()


if __name__ == "__main__":
    import sys

    try:
        option = sys.argv[1]

        if option == "add_users_and_posts":
            add_users_and_posts()
        elif option == "remove_users_and_posts":
            remove_users_and_posts()
        else:
            print("Please pass a valid option!")

    except IndexError:
        print("Please pass a valid option!")
    except KeyboardInterrupt:
        print("exiting...")