import subprocess
import os
import yaml
from pymongo import MongoClient
import requests
from itsdangerous import JSONWebSignatureSerializer
from datetime import datetime

from utils import strtobool
from utils.key import Key, KEY_DIR, get_secret_key
from utils.actor_service import ActorService
from utils.object_service import ObjectService

def noop():
    pass


CUSTOM_CACHE_HOOKS = False
try:
     from cache_hooks import purge as custom_cache_purge_hook
except ModuleNotFoundError:
    custom_cache_purge_hook = noop

VERSION = subprocess.check_output(['git', 'describe', '--always']).split()[0].decode('utf-8')

DEBUG_MODE = strtobool(os.getenv('MICROBLOGPUB_DEBUG', 'false'))


CTX_AS = 'https://www.w3.org/ns/activitystreams'
CTX_SECURITY = 'https://w3id.org/security/v1'
AS_PUBLIC = 'https://www.w3.org/ns/activitystreams#Public'
HEADERS = [
    'application/activity+json',
    'application/ld+json;profile=https://www.w3.org/ns/activitystreams',
    'application/ld+json; profile="https://www.w3.org/ns/activitystreams"',
    'application/ld+json',
]


with open(os.path.join(KEY_DIR, 'me.yml')) as f:
    conf = yaml.load(f)

    USERNAME = conf['username']
    NAME = conf['name']
    DOMAIN = conf['domain']
    SCHEME = 'https' if conf.get('https', True) else 'http'
    BASE_URL = SCHEME + '://' + DOMAIN
    ID = BASE_URL
    SUMMARY = conf['summary']
    ICON_URL = conf['icon_url']
    PASS = conf['pass']
    PUBLIC_INSTANCES = conf.get('public_instances', [])
    # TODO(tsileo): choose dark/light style
    THEME_COLOR = conf.get('theme_color')

USER_AGENT = (
        f'{requests.utils.default_user_agent()} '
        f'(microblog.pub/{VERSION}; +{BASE_URL})'
)

# TODO(tsileo): use 'mongo:27017;
# mongo_client = MongoClient(host=['mongo:27017'])
mongo_client = MongoClient(
        host=[os.getenv('MICROBLOGPUB_MONGODB_HOST', 'localhost:27017')],
)

DB_NAME = '{}_{}'.format(USERNAME, DOMAIN.replace('.', '_'))
DB = mongo_client[DB_NAME]

def _drop_db():
    if not DEBUG_MODE:
        return

    mongo_client.drop_database(DB_NAME)

KEY = Key(USERNAME, DOMAIN, create=True)


JWT_SECRET = get_secret_key('jwt')
JWT = JSONWebSignatureSerializer(JWT_SECRET)

def _admin_jwt_token() -> str:
    return JWT.dumps({'me': 'ADMIN', 'ts': datetime.now().timestamp()}).decode('utf-8')  # type: ignore

ADMIN_API_KEY = get_secret_key('admin_api_key', _admin_jwt_token)


ME = {
    "@context": [
        CTX_AS,
        CTX_SECURITY,
    ],
    "type": "Person",
    "id": ID,
    "following": ID+"/following",
    "followers": ID+"/followers",
    "liked": ID+"/liked",
    "inbox": ID+"/inbox",
    "outbox": ID+"/outbox",
    "preferredUsername": USERNAME,
    "name": NAME,
    "summary": SUMMARY,
    "endpoints": {},
    "url": ID,
    "icon": {
        "mediaType": "image/png",
        "type": "Image",
        "url": ICON_URL,
    },
    "publicKey": {
        "id": ID+"#main-key",
        "owner": ID,
        "publicKeyPem": KEY.pubkey_pem,
    },
}
print(ME)

ACTOR_SERVICE = ActorService(USER_AGENT, DB.actors_cache, ID, ME, DB.instances)
OBJECT_SERVICE = ObjectService(USER_AGENT, DB.objects_cache, DB.inbox, DB.outbox, DB.instances)
