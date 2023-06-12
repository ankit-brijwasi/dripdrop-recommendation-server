import datetime
import json
import os
import traceback

from appwrite.client import Client
from appwrite.id import ID
from appwrite.services.databases import Databases
from appwrite.services.users import Users
from appwrite.query import Query


def main(req, res):
    try:
        class Settings:
            APPWRITE_ENDPOINT = os.environ.get("APPWRITE_ENDPOINT")
            APPWRITE_PROJECT_ID = os.environ.get("APPWRITE_PROJECT_ID")
            APPWRITE_SECRET_KEY = os.environ.get("APPWRITE_SECRET_KEY")

            # collections
            APPWRITE_PROFILE_COLLECTION = os.environ.get("APPWRITE_PROFILE_COLLECTION")
            APPWRITE_POST_COLLECTION = os.environ.get("APPWRITE_POST_COLLECTION")
            APPWRITE_NOTIFICATION_COLLECTION = os.environ.get("APPWRITE_NOTIFICATION_COLLECTION")

            # databases
            APPWRITE_DATABASE_ID = os.environ.get("APPWRITE_DATABASE_ID")

            # storage
            APPWRITE_USER_DATA_STORAGE_ID = os.environ.get("APPWRITE_USER_DATA_STORAGE_ID")

        settings = Settings()
        client = Client()\
            .set_endpoint(settings.APPWRITE_ENDPOINT)\
            .set_project(settings.APPWRITE_PROJECT_ID)\
            .set_key(settings.APPWRITE_SECRET_KEY)

        databases = Databases(client)
        users = Users(client)

        payload = json.loads(req.payload)
        multiple = False
        data = {}

        if payload.get("action") == "like":
            post = databases.get_document(
                settings.APPWRITE_DATABASE_ID,
                settings.APPWRITE_POST_COLLECTION,
                payload["post_id"],
            )
            user = users.get(post.get("user_id")) # <--- user for whom notification is generated
            post_liked_by = databases.list_documents(
                settings.APPWRITE_DATABASE_ID,
                settings.APPWRITE_PROFILE_COLLECTION,
                [
                    Query.equal("user_id", payload["user_id"])
                ]
            ).get("documents")[0]

            if post.get("caption"):
                msg = f"{post_liked_by.get('username')} liked your post, {post.get('caption')}"
            else:
                msg = f"{post_liked_by.get('username')} liked your post"

            data.update({
                "user_id": user.get("$id"),
                "created_on": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "message": msg
            })

        elif payload.get("action") == "comment":
            post = databases.get_document(
                settings.APPWRITE_DATABASE_ID,
                settings.APPWRITE_POST_COLLECTION,
                payload["post_id"],
            )
            user = users.get(post.get("user_id")) # <--- user for whom notification is generated
            post_liked_by = databases.list_documents(
                settings.APPWRITE_DATABASE_ID,
                settings.APPWRITE_PROFILE_COLLECTION,
                [
                    Query.equal("user_id", payload["user_id"])
                ]
            ).get("documents")[0]

            if post.get("caption"):
                msg = f"{post_liked_by.get('username')} commented on your post, {post.get('caption')}"
            else:
                msg = f"{post_liked_by.get('username')} commented on your post"

            data.update({
                "user_id": user.get("$id"),
                "created_on": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "message": msg
            })
        
        elif payload.get("action") == "follow":
            profile = databases.get_document( # <---- user profile for that person who has followed
                settings.APPWRITE_DATABASE_ID,
                settings.APPWRITE_PROFILE_COLLECTION,
                payload["profile_id"],
            )
            followed_user_id = users.get(payload["followed_user_id"]) # <--- user for whom notification is generated

            msg = f"{profile.get('username')} has started following you!"
            data.update({
                "user_id": followed_user_id.get("$id"),
                "created_on": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "message": msg
            })

        elif payload.get("action") == "post-added":
            multiple = True
            post = databases.get_document(
                settings.APPWRITE_DATABASE_ID,
                settings.APPWRITE_POST_COLLECTION,
                payload["post_id"],
            )

            user_profile = databases.list_documents(
                settings.APPWRITE_DATABASE_ID,
                settings.APPWRITE_PROFILE_COLLECTION,
                [
                    Query.equal("user_id", post.get("user_id"))
                ]
            ).get("documents")[0]

            user = user_profile.get("following") + user_profile.get("followers")
            for following in list(set(user)):
                if following != "":
                    data[following] = {
                        "created_on": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "message": f"{user_profile.get('username')} added a new post"
                    }

        if multiple:
            for key, value in data.items():
                databases.create_document(
                    settings.APPWRITE_DATABASE_ID,
                    settings.APPWRITE_NOTIFICATION_COLLECTION,
                    ID.unique(),
                    {"user_id": key, **value}
                )

        else:
            databases.create_document(
                settings.APPWRITE_DATABASE_ID,
                settings.APPWRITE_NOTIFICATION_COLLECTION,
                ID.unique(),
                data
            )

        return res.json({'payload': "notification created"})
    except Exception as e:
        traceback.print_exc()
        return res.json({'payload': str(e)})
