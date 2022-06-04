# flask_iam

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](./LICENSE)
![GitHub latest tag](https://img.shields.io/github/v/tag/WildSys/flask_iam?sort=semver)

The `flask_iam` python project is a suggestion to implement Identity Access Management globally in a Flask application.

It generates IAM policies based on URL map (routes registered on Flask application) and controls access to an endpoint using the callback function you give.

This is not a package to manage users accounts. You keep the hand on policies to apply for each user (or group) and, obviously, the synchronisation between policies and your user database.

## Limitations (Read carefully)

- This package is developed and tested with Flask RESTX. Neither Flask or Flask RestPlus have been tested with it for now.
- The package is not yet submitted on PyPi, only available on this repository.

## Getting started

### Installation

```
pip install git+https://github.com/WildSys/flask_iam.git@0.1.0
```

(Of course, change the version if needed. Do not use `main` as it can be hazardous)

### A quick example

```
from flask import Flask
from flask_restx import Api, Resource
from flask_iam import IAM


def policy_check(policy_id):
    # Something here to check if current user can access to the policy.
    # Must returns True (allowed) or False (denied)
    return False


app = Flask(__name__)
api = Api(app)
iam = IAM(app, policy_check, undefined_policy_authorized=False)


@api.route('/test')
class MyResource(Resource):

    def get(self):
        """Get test resource"""
```

In the example above, the policy `test.read` while be automatically generated. And if you navigate to `GET /test`, you should get a `403 Forbidden` error.

You can also set `undefined_policy_authorized` option to `True` to allow non-resources scoped views (useful for Swagger documentation).

The method defines a default action: `GET` gives `read`, `POST` gives `create`, `DELETE` gives `delete` and `PUT` and `PATCH` gives `modify`.

However you can overwrite these presets with a decorator:

```
@api.route('/test')
class MyResource(Resource):

    @iam.rule(action='list')
    def get(self):
        """Get test resource"""
```

will give a `test.list` instead of `test.read`.

If you add resource in a *Namespace*, a level is automatically added to the policy (for example, you can have `iam.policies.list` if you have a method `get` in a class with route `/policies` in a Namespace prefxied with `/iam`, or, in URL representation, `GET /iam/policies`). Policy identifier is limited to 2 levels, keep it in mind and be imaginative in your application architecture and action naming convention.

You can also access to the list of auto-generated policies (returns a dictionary, key is policy ID and value is policy description):

```
policies = iam.list_policies()
```
