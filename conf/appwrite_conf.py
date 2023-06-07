from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.functions import Functions
from appwrite.services.storage import Storage
from appwrite.services.users import Users

from conf import settings


client = Client()\
    .set_endpoint(settings.APPWRITE_ENDPOINT)\
    .set_project(settings.APPWRITE_PROJECT_ID)\
    .set_key(settings.APPWRITE_SECRET_KEY)

databases = Databases(client)
users = Users(client)
functions = Functions(client)
storages = Storage(client)