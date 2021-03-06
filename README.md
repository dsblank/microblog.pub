# microblog.pub

<p align="center">
  <img 
    src="https://sos-ch-dk-2.exo.io/microblogpub/microblobpub.png" 
    width="200" height="200" border="0" alt="microblog.pub">
</p>
<p align="center">
<a href="https://travis-ci.org/tsileo/microblog.pub"><img src="https://travis-ci.org/tsileo/microblog.pub.svg?branch=master" alt="Build Status"></a>
<a href="https://github.com/tsileo/microblog.pub/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-AGPL_3.0-blue.svg?style=flat" alt="License"></a>
</p>

<p align="center">A self-hosted, single-user, <a href="https://activitypub.rocks">ActivityPub</a> powered microblog.</p>

**Still in early development.**

## Features

 - Implements a basic [ActivityPub](https://activitypub.rocks/) server (with federation)
   - Compatible with [Mastodon](https://github.com/tootsuite/mastodon) and others (Pleroma, Hubzilla...)
   - Also implements a remote follow compatible with Mastodon instances
 - Exposes your outbox as a basic microblog
 - Implements [IndieAuth](https://indieauth.spec.indieweb.org/) endpoints (authorization and token endpoint)
   - U2F support
   - You can use your ActivityPub identity to login to other websites/app
 - Admin UI with notifications and the stream of people you follow
 - Allows you to attach files to your notes
   - Privacy-aware image upload endpoint that strip EXIF meta data before storing the file
 - No JavaScript, that's it, even the admin UI is pure HTML/CSS
 - Easy to customize (the theme is written Sass)
   - mobile-friendly theme
   - with dark and light version
 - Microformats aware (exports `h-feed`, `h-entry`, `h-cards`, ...)
 - Exports RSS/Atom feeds
 - Comes with a tiny HTTP API to help posting new content and performing basic actions
 - Easy to "cache" (the external/public-facing microblog part)
   - With a good setup, cached content can be served most of the time
   - You can setup a "purge" hook to let you invalidate cache when the microblog was updated
 - Deployable with Docker (Docker compose for everything: dev, test and deployment)
 - Focus on testing
   - Tested against the [official ActivityPub test suite](https://test.activitypub.rocks/) ([ ] TODO submit the report)
   - CI runs some local "federation" tests
   - Manually tested against [Mastodon](https://github.com/tootsuite/mastodon)
   - Project is running an up-to-date instance

## ActivityPub

microblog.pub implements an [ActivityPub](http://activitypub.rocks/) server, it implements both the client to server API and the federated server to server API.

Compatible with [Mastodon](https://github.com/tootsuite/mastodon) (which is not following the spec closely), but will drop OStatus messages.

Activities are verified using HTTP Signatures or by fetching the content on the remote server directly.

## Running your instance

### Installation

```shell
$ git clone
$ make css
$ cp -r config/me.sample.yml config/me.yml
``` 

### Configuration

```shell
$ make password
```

### Deployment

```shell
$ docker-compose up -d
```

## Development

The most convenient way to hack on microblog.pub is to run the server locally, and run


```shell
# One-time setup
$ pip install -r requirements.txt
# Start the Celery worker, RabbitMQ and MongoDB
$ docker-compose -f docker-compose-dev.yml up -d
# Run the server locally
$ MICROBLOGPUB_DEBUG=1 FLASK_APP=app.py flask run -p 5005 --with-threads
```

## ActivityPub API

### GET /

Returns the actor profile, with links to all the "standard" collections.

### GET /tags/:tag

Special collection that reference notes with the given tag.

### GET /stream

Special collection that returns the stream/inbox as displayed in the UI.

## User API

The user API is used by the admin UI (and requires a CSRF token when used with a regular user session), but it can also be accessed with an API key.

All the examples are using [HTTPie](https://httpie.org/).

### POST /api/note/delete{?id}

Deletes the given note `id` (the note must from the instance outbox).

Answers a **201** (Created) status code.

You can pass the `id` via JSON, form data or query argument.

#### Example

```shell
$ http POST https://microblog.pub/api/note/delete Authorization:'Bearer <token>' id=http://microblob.pub/outbox/<note_id>/activity
```

#### Response

```json
{
    "activity": "https://microblog.pub/outbox/<delete_id>"
}
```

### POST /api/like{?id}

Likes the given activity.

Answers a **201** (Created) status code.

You can pass the `id` via JSON, form data or query argument.

#### Example

```shell
$ http POST https://microblog.pub/api/like Authorization:'Bearer <token>' id=http://activity-iri.tld
```

#### Response

```json
{
    "activity": "https://microblog.pub/outbox/<like_id>"
}
```

### POST /api/boost{?id}

Boosts/Announces the given activity.

Answers a **201** (Created) status code.

You can pass the `id` via JSON, form data or query argument.

#### Example

```shell
$ http POST https://microblog.pub/api/boost Authorization:'Bearer <token>' id=http://activity-iri.tld
```

#### Response

```json
{
    "activity": "https://microblog.pub/outbox/<announce_id>"
}
```

### POST /api/block{?actor}

Blocks the given actor, all activities from this actor will be dropped after that.

Answers a **201** (Created) status code.

You can pass the `id` via JSON, form data or query argument.

#### Example

```shell
$ http POST https://microblog.pub/api/block Authorization:'Bearer <token>' actor=http://actor-iri.tld/
```

#### Response

```json
{
    "activity": "https://microblog.pub/outbox/<block_id>"
}
```

### POST /api/follow{?actor}

Follows the given actor.

Answers a **201** (Created) status code.

You can pass the `id` via JSON, form data or query argument.

#### Example

```shell
$ http POST https://microblog.pub/api/follow Authorization:'Bearer <token>' actor=http://actor-iri.tld/
```

#### Response

```json
{
    "activity": "https://microblog.pub/outbox/<follow_id>"
}
```

### POST /api/new_note{?content,reply}

Creates a new note. `reply` is the IRI of the "replied" note if any.

Answers a **201** (Created) status code.

You can pass the `content` and `reply` via JSON, form data or query argument.

#### Example

```shell
$ http POST https://microblog.pub/api/new_note Authorization:'Bearer <token>' content=hello
```

#### Response

```json
{
    "activity": "https://microblog.pub/outbox/<create_id>"
}
```


### GET /api/stream


#### Example

```shell
$ http GET https://microblog.pub/api/stream Authorization:'Bearer <token>'
```

#### Response

```json
```


## Contributions

PRs are welcome, please open an issue to start a discussion before your start any work.
