import random

from appwrite.services.account import Account
from fastapi import FastAPI, Response, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from conf.appwrite_conf import client
from prepare_dataset import get_posts_from_db, get_profiles_from_db

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/recommend/accounts/")
def recommend_accounts(access_token: str = Header(title="access_token"), limit: int = 25, offset: int = 0):
    if not access_token:
        return Response('{"detail": "No access token was provided"}', 401)

    client.set_jwt(access_token)
    account = Account(client)

    try:
        user = account.get()
        profiles = get_profiles_from_db()
        profiles["documents"] = list(filter(
            lambda profile: not profile.get("user_id") == user.get("$id"),
            profiles["documents"]
        ))
        profiles["documents"] = list(filter(
            lambda profile: user.get("$id") not in profile["followers"],
            profiles["documents"]
        ))
        profiles["documents"] = list(filter(
            lambda profile: user.get("$id") not in profile["following"],
            profiles["documents"]
        ))

        profiles["documents"] = sorted(
            profiles["documents"],
            key=lambda profile: len(profile["following"]),
            reverse=True
        )
        return profiles
    except Exception:
        return Response(
            '{"detail": "No access token was provided"}',
            401
        )


@app.get("/recommend/posts/")
def recommend_posts(access_token: str = Header(title="access_token"), limit: int = 25, offset: int = 0):
    if not access_token:
        return JSONResponse(
            '{"detail": "No access token was provided"}',
            401
        )
    
    client.set_jwt(access_token)
    account = Account(client)
    try:
        account.get()
        posts = get_posts_from_db(limit, offset)
        # posts["documents"] = list(
        #     filter(
        #         lambda post: user.get("$id") not in post["liked_by"],
        #         posts["documents"]
        #     )
        # )

        # posts["documents"] = list(
        #     filter(
        #         lambda post: user.get("$id") not in post["comments"],
        #         posts["documents"]
        #     )
        # )

        # posts["documents"] = list(
        #     filter(
        #         lambda post: user.get("$id") not in post["saved_by"],
        #         posts["documents"]
        #     )
        # )
        # random.shuffle(posts["documents"])
        return posts

    except Exception as e:
        import traceback
        print(e)
        traceback.print_exc()
        return Response(
            '{"detail": "No access token was provided"}',
            401
        )
