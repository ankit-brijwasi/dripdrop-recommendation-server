from appwrite.query import Query
from conf import settings

from conf.appwrite_conf import databases


def get_posts_from_db(limit = 25, offset = 0):
    fetched_posts = databases.list_documents(
        settings.APPWRITE_DATABASE_ID,
        settings.APPWRITE_POST_COLLECTION,
        [
            Query.limit(limit),
            Query.offset(offset),
            Query.order_asc("posted_on")
        ],
    )
    return fetched_posts


def get_profiles_from_db(limit = 0, offset = 0):
    fetched_profiles = databases.list_documents(
        settings.APPWRITE_DATABASE_ID,
        settings.APPWRITE_PROFILE_COLLECTION,
        [
            Query.limit(limit),
            Query.offset(offset)
        ],
    )
    return fetched_profiles

