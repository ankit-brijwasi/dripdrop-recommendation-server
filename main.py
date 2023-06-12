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
def recommend_accounts(access_token: str = Header(title="access_token"), limit: int = 15, offset: int = 0):
    if not access_token:
        return Response('{"detail": "No access token was provided"}', 401)

    client.set_jwt(access_token)
    account = Account(client)

    try:
        user = account.get()
        profiles = get_profiles_from_db()

        for document in profiles["documents"]:
            document["followers"] = list(filter(bool, document["followers"]))
            document["following"] = list(filter(bool, document["following"]))

        profiles["documents"] = list(
            filter(
                lambda profile: not profile.get("user_id") == user.get("$id"),
                profiles["documents"]
            )
        )
        profiles["documents"] = sorted(
            profiles["documents"],
            key=lambda profile: len(profile["following"]),
            reverse=True
        )
        return profiles
    except Exception as e:
        print(e)
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
        return posts

    except Exception as e:
        import traceback
        print(e)
        traceback.print_exc()
        return Response(
            '{"detail": "No access token was provided"}',
            401
        )
