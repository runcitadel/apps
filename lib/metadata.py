# SPDX-FileCopyrightText: 2021 Aaron Dewes <aaron.dewes@protonmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-only

import os
import yaml

# Creates a registry with just the things we need in the update checker so we can remove registry.json from this repo.
# We need these properties: id, name, repo, version, nothing else. We don't need to check for the existence of these properties.
# app_yml['metadata'] may contain other properties, but we don't need them and we remove them from the registry.
def getSimpleAppRegistry(apps, app_path):
    app_metadata = []
    for app in apps:
        app_yml_path = os.path.join(app_path, app, 'app.yml')
        if os.path.isfile(app_yml_path):
            with open(app_yml_path, 'r') as f:
                app_yml = yaml.safe_load(f.read())
                metadata = {
                    'id': app,
                    'name': app_yml['metadata']['name'],
                    'repo': app_yml['metadata']['repo'],
                    'version': app_yml['metadata']['version']
                }
                app_metadata.append(metadata)
    return app_metadata
