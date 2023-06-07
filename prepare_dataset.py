from appwrite.query import Query
from conf import settings

from conf.appwrite_conf import databases


def get_posts_from_db(posts_fetched = 0, prev_posts = []):
    fetched_posts = databases.list_documents(
        settings.APPWRITE_DATABASE_ID,
        settings.APPWRITE_POST_COLLECTION,
        [
            Query.limit(25),
            Query.offset(posts_fetched)
        ],
    )
    total = fetched_posts.get("total")

    if posts_fetched <= total:
        prev_posts += [doc for doc in fetched_posts.get("documents")]
        return get_posts_from_db(posts_fetched + 25, prev_posts)

    return prev_posts


def get_profiles_from_db(profiles_fetched = 0, prev_profiles = []):
    fetched_profiles = databases.list_documents(
        settings.APPWRITE_DATABASE_ID,
        settings.APPWRITE_PROFILE_COLLECTION,
        [
            Query.limit(25),
            Query.offset(profiles_fetched)
        ],
    )
    total = fetched_profiles.get("total")

    if profiles_fetched <= total:
        prev_profiles += [doc for doc in fetched_profiles.get("documents")]
        return get_profiles_from_db(profiles_fetched + 25, prev_profiles)

    return prev_profiles

