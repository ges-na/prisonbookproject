from django.contrib.admin import AdminSite as DjAdminSite


class AdminSite(DjAdminSite):
    # Source - https://stackoverflow.com/a/77422142
    # Posted by FreedomRings, modified by community. See post 'Timeline' for change history
    # Retrieved 2026-06-08, License - CC BY-SA 4.0

    def get_app_list(self, request, app_label=None):

        if not app_label:
            # The order of the apps is set here (use the app_label name):
            app_order = ["auth", "app", "issues"]
            app_order_dict = dict(zip(app_order, range(len(app_order))))
            app_list = list(self._build_app_dict(request).values())
            app_list.sort(key=lambda x: app_order_dict.get(x["app_label"], 0))
        else:
            # Everything is sorted alphabetically by app and within each app.
            app_dict = self._build_app_dict(request, app_label)
            app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())

        # Iterate down the app list and set the presentation order of the models:
        auth_models = []
        app_models = []
        issue_models = []
        for app in app_list:
            for model in app["models"]:
                if model["object_name"] == "User":
                    auth_models.append(model)
                elif model["object_name"] == "LetterIssue":
                    issue_models.append(model)
                elif model["object_name"] == "PersonIssue":
                    issue_models.append(model)
                elif app["app_label"] == "auth":
                    auth_models.append(model)
                elif app["app_label"] == "app":
                    app_models.append(model)

        new_app_list = []
        for app in app_list:
            if app["app_label"] == "auth":
                app["models"] = auth_models
                new_app_list.append(app)
            elif app["app_label"] == "app":
                app["models"] = app_models
                new_app_list.append(app)

        new_app_list.append(
            {
                "name": "Issues",
                "app_label": "issues",
                "app_url": "",
                "has_module_perms": True,
                "models": issue_models,
            }
        )

        return new_app_list
