#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports
from flask import request
from flask.app import Flask as FlaskApp
from werkzeug.exceptions import Forbidden
from .decorators import setupmethod, FUNC
from urllib.parse import urlparse


class IAM:
    flask_app = None
    disable_filtering = False
    permission_callback = None
    undefined_policy_authorized = False
    scopes = None
    rules = []

    def __init__(self, flask_app, permission_callback, **kwargs):
        assert isinstance(flask_app, FlaskApp), 'Not a valid Flask application'
        assert callable(permission_callback), 'Not a callable function for permission_callback'
        self.flask_app = flask_app
        self.permission_callback = permission_callback
        self.undefined_policy_authorized = kwargs.get('undefined_policy_authorized', False)
        self.trigger_iam_validation()

        def rule(f):
            def wrapper(*args, **kwargs):
                self.set_rule(*args, **kwargs)
            return wrapper

    def trigger_iam_validation(self):
        """Register interceptors for IAM"""
        self.flask_app.before_request(self.check_iam_permission)

    def check_iam_permission(self):
        """Validate access"""
        if self.disable_filtering is False:
            adapter = self.flask_app.url_map.bind(urlparse(request.base_url).hostname)
            match = None
            try:
                match = adapter.match(request.path, method=request.method)[0]
            except Exception:
                pass
            name = self.get_endpoint_name(match, request.method)
            scope = []
            if name:
                scope = [x for x in self.list_policies(raw=True) if x['function'] == name]
            if len(scope) == 1:
                if not self.permission_callback(scope[0]['name']):
                    raise Forbidden()
            elif not self.undefined_policy_authorized:
                raise Forbidden()

    def get_policy_description(self, policy):
        infos = policy.split('.')
        desc = f'Allow to {infos[-1]} {infos[-2]}'
        return desc

    def get_endpoint_name(self, endpoint, method):
        func_data = self.flask_app.view_functions.get(endpoint, None)
        if func_data is None:
            return None
        name = func_data.__qualname__ if hasattr(func_data, '__qualname__') else func_data.__name__
        if hasattr(func_data, 'view_class'):
            name = func_data.view_class.__qualname__
        name = f'{name}.{method.lower()}'
        return name

    def list_policies(self, **kwargs):
        # "list" and other actions MUST be defined using decorator @iam.rule
        raw_mode = kwargs.get('raw', False)
        _methods_actions = {
            'GET': 'read',
            'POST': 'create',
            'PATCH': 'modify',
            'PUT': 'modify',
            'DELETE': 'delete'
        }
        _methods_skip = ['HEAD', 'OPTIONS']
        scopes = {}
        for rule in self.flask_app.url_map.iter_rules():
            if rule.endpoint.endswith('_resource'):
                for method in rule.methods:
                    if method in _methods_skip:
                        continue
                    action = _methods_actions.get(method, 'undefined')
                    levels = '.'.join(str(rule).strip('/').split('/')[0:2])
                    name = self.get_endpoint_name(rule.endpoint, method)
                    if not name:
                        continue
                    overwrite = [x for x in self.rules if x['function'] == name]
                    if len(overwrite):
                        options = overwrite[0].get('options', {})
                        action = options.get('action', action)
                    scope = f'{levels}.{action}'
                    scopes[scope] = {
                        'name': scope,
                        'description': self.get_policy_description(scope),
                        'function': name
                    }
        if raw_mode:
            return list(scopes.values())
        else:
            return dict(sorted({x['name']: x['description'] for x in scopes.values()}.items()))

    @setupmethod
    def rule(self, *args, **kwargs):
        """Set specific IAM rule on an endpoint"""

        def decorator(f: FUNC) -> FUNC:
            self.rules.append({
                'module': f.__module__,
                'function': f.__qualname__,
                'options': kwargs
            })
            return f

        return decorator
