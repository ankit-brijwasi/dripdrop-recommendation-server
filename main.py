from appwrite.services.account import Account
from fastapi import FastAPI, Response, Header
from fastapi.responses import JSONResponse
from conf.appwrite_conf import client
from prepare_dataset import get_posts_from_db, get_profiles_from_db

app = FastAPI()

@app.get("/recommend/accounts/")
def recommend_accounts(access_token: str = Header(title="access_token"), top_n: int = 10):
    if not access_token:
        return Response('{"detail": "No access token was provided"}', 401)

    client.set_jwt(access_token)
    account = Account(client)

    try:
        user = account.get()
        profiles = get_profiles_from_db()
        profiles = list(filter(
            lambda profile: not profile.get("user_id") == user.get("$id"),
            profiles
        ))
        profiles = list(filter(
            lambda profile: user.get("$id") not in profile["followers"],
            profiles
        ))
        profiles = list(filter(
            lambda profile: user.get("$id") not in profile["following"],
            profiles
        ))

        profiles = sorted(
            profiles,
            key=lambda profile: len(profile["following"]),
            reverse=True
        )
        return profiles[:top_n]
    except Exception:
        return Response(
            '{"detail": "No access token was provided"}',
            401
        )

@app.get("/recommend/posts/")
def recommend_posts(access_token: str = Header(title="access_token"), top_n: int = 10):
    if not access_token:
        return JSONResponse(
            '{"detail": "No access token was provided"}',
            401
        )
    
    client.set_jwt(access_token)
    account = Account(client)

    try:
        user = account.get()
        posts = get_posts_from_db()
        posts = list(filter(lambda post: user.get("$id") not in post["liked_by"], posts))
        posts = list(filter(lambda post: user.get("$id") not in post["comments"], posts))
        posts = list(filter(lambda post: user.get("$id") not in post["saved_by"], posts))

        posts = sorted(posts, key=lambda post: len(post["liked_by"]), reverse=True)
        return posts[:top_n]
    except Exception:
        return Response(
            '{"detail": "No access token was provided"}',
            401
        )
