# wedo API

This API serves as the bridge between bot and web, enabling database access

The common objects are Events, Guests, and Invites.

- [wedo API](#wedo-api)
  - [Endpoints](#endpoints)
    - [Responses](#responses)
    - [Events](#events)
      - [Get Events](#get-events)
      - [Get Event by ID](#get-event-by-id)
      - [Create Event](#create-event)
    - [Invites](#invites)
      - [Get Invites](#get-invites)
      - [Get Invite by ID](#get-invite-by-id)
      - [Create Invite](#create-invite)
      - [Edit Invite by ID](#edit-invite-by-id)
      - [Delete Invite](#delete-invite)
    - [Guests](#guests)
      - [Get Guests](#get-guests)
      - [Get Guest by ID](#get-guest-by-id)
      - [Create Guest](#create-guest)
      - [Edit Guest by ID](#edit-guest-by-id)
      - [Assign Guest to Invite](#assign-guest-to-invite)
      - [Unassign Guest from Invite](#unassign-guest-from-invite)
  - [Development Guide](#development-guide)
    - [Setup](#setup)
    - [Testing](#testing)
    - [Models](#models)
      - [Database Patterns](#database-patterns)

## Endpoints

### Responses

The following exception status codes are possible

Code | Description | Explanation
--- | --- | ---
400 | Bad Request | The request was malformed. Check the request parameters or body
401 | Unauthorized | The request was not authorized
404 | Not Found | The requested endpoint or record was not located on the server
422 | Unprocessible Entity | The server understood your request but was unable to proceed. You may try again later
500 | Internal Server Error | The server encountered an error processing your request

### Events

Represents a timeboxed, attendable event

```json
{
    "id": 1,
    "name": "Wedding Lunch",
    "address": "123 Main St, Aurora, CO 80011, United States of America",
    "start_datetime": "2020-02-14 12:00:00",
    "end_datetime": "2020-02-14 14:00:00",
    "invites": [
        "{Invite}"
    ]
}
```

#### Get Events

`GET` /api/v1/events

```json
{
    "success": true,
    "events": [
        "{Event}"
    ]
}
```

#### Get Event by ID

`GET` /api/v1/events/{id}

id: ID of event

```json
{
    "success": true,
    "event": "{Event}"
}
```

#### Create Event

`POST` /api/v1/events

> Note: Invites can only be added to Events via the Invites API

```json
{
    "name": "Wedding Lunch",
    "address": "123 Main St, Aurora, CO 80011, United States of America",
    "start_datetime": "2020-02-14 12:00:00",
    "end_datetime": "2020-02-14 14:00:00"
}
```

Response:

```json
{
    "success": true,
    "event": "{Event}"
}
```

### Invites

```json
{
    "id": 1,
    "guests": [
        "{Guest}"
    ],
    "accepted": false,
    "event_id": 1,
    "invite_code": "A1B2C3"
}
```

#### Get Invites

`GET` /api/v1/invites

```json
{
    "success": true,
    "invites": [
        "{Invite}"
    ]
}
```

#### Get Invite by ID

`GET` /api/v1/invites/{id}

id: ID of invite

```json
{
    "success": true,
    "invite": "{Invite}"
}
```

#### Create Invite

`POST` /api/v1/invites

> Note: Guests can only be added to Invites via the Guests API

```json
{
    "accepted": false,
    "event_id": 1
}
```

Response:

```json
{
    "success": true,
    "invite": "{Invite}"
}
```

#### Edit Invite by ID

`PATCH` /api/v1/invites/{id}

> Note: Guests can only be edited on Invites via the Guests API. See `Assign Guest to Invite` or `Unassign Guest to Invite`

id: ID of invite

```json
{
    "accepted": true,
    "event_id": 2
}
```

#### Delete Invite

`DELETE` /api/v1/invites/{id}

id: ID of guest

Response:

```json
{
    "success": true
}
```

### Guests

```json
{
    "id": 1,
    "name": "John Doe",
    "invite_id": 1,
    "telegram_username": "username"
}
```

#### Get Guests

`GET` /api/v1/guests

```json
{
    "success": true,
    "guests": [
        "{Guest}"
    ]
}
```

#### Get Guest by ID

`GET` /api/v1/guests/{id}

id: ID of guest

```json
{
    "success": true,
    "guest": "{Guest}"
}
```

#### Create Guest

`POST` /api/v1/guests

> Note: Invites can only be added to Guests via another method in the Guests API. See `Assign Guest to Invite`

```json
{
    "name": "John Doe",
    "telegram_username": "john"
}
```

Response:

```json
{
    "success": true,
    "guest": "{Guest}"
}
```

#### Edit Guest by ID

`PATCH` /api/v1/guests/{id}

> Note: Invites can only be edited on Guests via another method in the Guests API. See `Assign Guest to Invite` or `Unassign Guest to Invite`

id: ID of guest

```json
{
    "name": "John Doe",
    "telegram_username": "username"
}
```

Response:

```json
{
    "success": true,
    "guest": "{Guest}"
}
```

#### Assign Guest to Invite

`POST` /api/v1/guests/{id}/invites

id: ID of guest

```json
{
    "invite_id": 1
}
```

Response:

```json
{
    "success": true,
    "guest": "{Guest}"
}
```

#### Unassign Guest from Invite

`DELETE` /api/v1/guests/{id}/invites

id: ID of guest

Response:

```json
{
    "success": true,
    "guest": "{Guest}"
}
```

## Development Guide

### Setup

This project runs on Pipenv

```shell
pip install pipenv
```

For the time being, this API is secured by Auth0. Visit [Auth0](https://www.auth0.com) for more information on how to set up your account.

Ensure that you have a `.env` file with the following structure

```env
AUTH0_DOMAIN={auth0_domain}.auth0.com
API_AUDIENCE={auth0_audience}
FLASK_APP=api.py
SQLALCHEMY_DATABASE_URI=postgres://{username}@{host}:{port}/api
```

At first run, please create the database like so

```shell
psql {user}
CREATE DATABASE api;
```

The app will automatically create the relations listed in `models.py` if not already created.

Run the app using `pipenv run flask run`

### Testing

A Postman collection has been provided for testing. After importing to Postman, remember to edit the Authorization token of the collection to use the JWT token generated by Auth0.

### Models

#### Database Patterns

- Guests can be invited to an Event (many to one)
- Guests must be invited through an Invite (many to one)
- An Event can have many Invites (one to many)
