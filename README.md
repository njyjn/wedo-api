# wedo API

This API is part of a larger project called Wedo, a guest registration and event management interface for my wedding. The API interfaces to the Events, Guests, and Invites database for the occasion, serving as the bridge between the other bot and web interfaces. As this is an API module, there is no UI.

- [wedo API](#wedo-api)
  - [Development Guide](#development-guide)
    - [Setup](#setup)
    - [Testing](#testing)
    - [Models](#models)
      - [Database Patterns](#database-patterns)
  - [Endpoints](#endpoints)
    - [Roles](#roles)
    - [Responses](#responses)
    - [Events](#events)
      - [Get Events](#get-events)
      - [Get Event by ID](#get-event-by-id)
      - [Create Event](#create-event)
      - [Edit Event by ID](#edit-event-by-id)
      - [Delete Event](#delete-event)
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

## Development Guide

### Setup

This project runs using a Pipenv virtual environment. A `requirements.txt` file is also provided in case you want to run the project on other virtual environments.

```shell
pip install pipenv
```

You may use the provided `init.sh` script to export the necessary environment variables. Before running the project, edit the file with your config options.

```shell
chmod +x ./init.sh
source ./init.sh
```

Run the project within a Pipenv shell or a virtual environment of your choosing.

```shell
pipenv shell
```

For the time being, this API is secured by Auth0. Visit [Auth0](https://www.auth0.com) for more information on how to set up your account.

At first run, create the database like so.

```shell
psql {user}
CREATE DATABASE api;
```

The app will automatically create the relations listed in `models.py` if not already created.

Run the app using `pipenv run flask run`

If you are testing, use a separate database with the instructions provided in the next section.

### Testing

A Postman collection `WedoAPI.postman_collection.json` has been provided for testing. Before running the collection, run the script `pretest.sh` to prepare the database.

```shell
source ./pretest.sh
```

### Models

#### Database Patterns

- Guests can be invited to an Event (many to one)
- Guests must be invited through an Invite (many to one)
- An Event can have many Invites (one to many)

## Endpoints

### Roles

The following roles are available in the app

- read:events
- read:guests
- read:invites
- create:events
- create:guests
- create:invites

The *admin* user has access to all roles, whereas the *guest* user has access to only the `read` roles.

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
Roles: read:events

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
Roles: read:events

id: ID of event

```json
{
    "success": true,
    "event": "{Event}"
}
```

#### Create Event

`POST` /api/v1/events
Roles: create:events

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

#### Edit Event by ID

`PATCH` /api/v1/events/{id}
Roles: create:events

id: ID of event

```json
  {
      "name": "Wedding Dinner",
      "address": "123 Main Blvd, Aurora, CO 80011",
      "start_datetime": "2050-01-01T18:00:00-06:00",
      "end_datetime": "2050-01-01T23:00:00-06:00",
  }
```

Response:

```json
{
    "success": true,
    "event": "{Event}"
}
```

#### Delete Event

`DELETE` /api/v1/events/{id}
Roles: create:events

id: ID of event

Response:

```json
{
    "success": true
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
Roles: read:invites

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
Roles: read:invites

id: ID of invite

```json
{
    "success": true,
    "invite": "{Invite}"
}
```

#### Create Invite

`POST` /api/v1/invites
Roles: create:invites

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
Roles: create:invites

> Note: Guests can only be edited on Invites via the Guests API. See `Assign Guest to Invite` or `Unassign Guest to Invite`

id: ID of invite

```json
{
    "accepted": true,
    "event_id": 2
}
```

Response:

```json
{
    "success": true,
    "invite": "{Invite}"
}
```

#### Delete Invite

`DELETE` /api/v1/invites/{id}
Roles: create:invites

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
Roles: read:guests

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
Roles: read:guests

id: ID of guest

```json
{
    "success": true,
    "guest": "{Guest}"
}
```

#### Create Guest

`POST` /api/v1/guests
Roles: create:guests

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
Roles: create:guests

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
Roles: create:guests

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
Roles: create:guests

id: ID of guest

Response:

```json
{
    "success": true,
    "guest": "{Guest}"
}
```
