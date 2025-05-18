## misc

- [ ] maybe add support for https://logon.kegs.org.uk/adfs/portal/updatepassword/
- [ ] Requests wrapper?

## Library

- [ ] News: https://kegs.oliverasp.co.uk/library/home/api/news

# vle

## https://vle.kegs.org.uk/tag/index.php

`GET`

Get an HTML page relating to the tag

Query parameters:

```py
params = {
    "tag": "<tag name>"
}
```

Data to scrape:

- title
- Description (as html)
- related tags
- related blogposts (there is a JSON endpoint for this)
- People interested (there is a JSON endpoint for this)

## https://vle.kegs.org.uk/lib/ajax/service.php

`POST`

Get a list of tagged blog posts

Query parameters:

```py
params = {
    "sesskey": "<sesskey>",
    "info": "core_tag_get_tagindex"
}
```

Request payload (JSON):

```py
payload_json = [{
    "index": 0,  # idk what this is
    "methodname": "core_tag_get_tagindex",
    "args": {
        "tagindex": {
            "tc": "1",  # idk what this is, comes with link to blog post as query param, doesn't seem to serve a purpose
            "tag": "<tag name>",
            "ta": "7",  # idk what this is, seems to be consistent
            "page": "<page idx as string ig>"}
    }}]
```

example response:

```JSON
[
  {
    "error": false,
    "data": {
      "tagid": 643,
      "ta": 7,
      "component": "core",
      "itemtype": "post",
      "nextpageurl": "https:\/\/vle.kegs.org.uk\/tag\/index.php?tc=1&tag=Woodlouse&ta=7&page=4",
      "prevpageurl": "https:\/\/vle.kegs.org.uk\/tag\/index.php?tc=1&tag=Woodlouse&ta=7&page=2",
      "exclusiveurl": "https:\/\/vle.kegs.org.uk\/blog\/index.php?tagid=643",
      "exclusivetext": "Show only tagged Blog posts",
      "title": "Blog posts",
      "content": "<ul class=\"tag_feed media-list\">\n        <li class=\"media\">\n                <div class=\"itemimage\">\n                    <a href=\"https:\/\/vle.kegs.org.uk\/user\/profile.php?id=3207\"><img src=\"https:\/\/vle.kegs.org.uk\/pluginfile.php\/22723\/user\/icon\/trema\/f2?rev=105197\" class=\"userpicture\" width=\"35\" height=\"35\" alt=\"Picture of Oliver Edwards\" title=\"Picture of Oliver Edwards\" \/><\/a>\n                <\/div>\n            <div class=\"media-body\">\n                    <div class=\"media-heading\">\n                        <a class=\"\" href=\"https:\/\/vle.kegs.org.uk\/blog\/index.php?entryid=49\">Language of the day TWO - maltese<\/a>\n                    <\/div>\n                    <div class=\"muted\">\n                        <a href=\"https:\/\/vle.kegs.org.uk\/user\/view.php?id=3207\">Oliver Edwards<\/a>, Tuesday, 23 April 2024, 9:35 PM\n                    <\/div>\n            <\/div>\n        <\/li>\n        <li class=\"media\">\n                <div class=\"itemimage\">\n                    <a href=\"https:\/\/vle.kegs.org.uk\/user\/profile.php?id=3289\"><img src=\"https:\/\/vle.kegs.org.uk\/pluginfile.php\/22925\/user\/icon\/trema\/f2?rev=105591\" class=\"userpicture\" width=\"35\" height=\"35\" alt=\"Picture of Fraser Holmes\" title=\"Picture of Fraser Holmes\" \/><\/a>\n                <\/div>\n            <div class=\"media-body\">\n                    <div class=\"media-heading\">\n                        <a class=\"\" href=\"https:\/\/vle.kegs.org.uk\/blog\/index.php?entryid=47\">Have you ever tasted it<\/a>\n                    <\/div>\n                    <div class=\"muted\">\n                        <a href=\"https:\/\/vle.kegs.org.uk\/user\/view.php?id=3289\">Fraser Holmes<\/a>, Tuesday, 23 April 2024, 9:34 PM\n                    <\/div>\n            <\/div>\n        <\/li>\n        <li class=\"media\">\n                <div class=\"itemimage\">\n                    <a href=\"https:\/\/vle.kegs.org.uk\/user\/profile.php?id=3207\"><img src=\"https:\/\/vle.kegs.org.uk\/pluginfile.php\/22723\/user\/icon\/trema\/f2?rev=105197\" class=\"userpicture\" width=\"35\" height=\"35\" alt=\"Picture of Oliver Edwards\" title=\"Picture of Oliver Edwards\" \/><\/a>\n                <\/div>\n            <div class=\"media-body\">\n                    <div class=\"media-heading\">\n                        <a class=\"\" href=\"https:\/\/vle.kegs.org.uk\/blog\/index.php?entryid=45\">Language of the day ONE - CORNISH<\/a>\n                    <\/div>\n                    <div class=\"muted\">\n                        <a href=\"https:\/\/vle.kegs.org.uk\/user\/view.php?id=3207\">Oliver Edwards<\/a>, Tuesday, 23 April 2024, 9:16 PM\n                    <\/div>\n            <\/div>\n        <\/li>\n        <li class=\"media\">\n                <div class=\"itemimage\">\n                    <a href=\"https:\/\/vle.kegs.org.uk\/user\/profile.php?id=3355\"><img src=\"https:\/\/vle.kegs.org.uk\/pluginfile.php\/23983\/user\/icon\/trema\/f2?rev=105141\" class=\"userpicture\" width=\"35\" height=\"35\" alt=\"Cho Man\" title=\"Cho Man\" \/><\/a>\n                <\/div>\n            <div class=\"media-body\">\n                    <div class=\"media-heading\">\n                        <a class=\"\" href=\"https:\/\/vle.kegs.org.uk\/blog\/index.php?entryid=43\">My story about Aman Gupta, Aryan Pradeep and maybe some others.<\/a>\n                    <\/div>\n                    <div class=\"muted\">\n                        <a href=\"https:\/\/vle.kegs.org.uk\/user\/view.php?id=3355\">Edward James<\/a>, Tuesday, 23 April 2024, 9:10 PM\n                    <\/div>\n            <\/div>\n        <\/li>\n        <li class=\"media\">\n                <div class=\"itemimage\">\n                    <a href=\"https:\/\/vle.kegs.org.uk\/user\/profile.php?id=3289\"><img src=\"https:\/\/vle.kegs.org.uk\/pluginfile.php\/22925\/user\/icon\/trema\/f2?rev=105591\" class=\"userpicture\" width=\"35\" height=\"35\" alt=\"Picture of Fraser Holmes\" title=\"Picture of Fraser Holmes\" \/><\/a>\n                <\/div>\n            <div class=\"media-body\">\n                    <div class=\"media-heading\">\n                        <a class=\"\" href=\"https:\/\/vle.kegs.org.uk\/blog\/index.php?entryid=41\">the scariest stories: a thread<\/a>\n                    <\/div>\n                    <div class=\"muted\">\n                        <a href=\"https:\/\/vle.kegs.org.uk\/user\/view.php?id=3289\">Fraser Holmes<\/a>, Tuesday, 23 April 2024, 9:09 PM\n                    <\/div>\n            <\/div>\n        <\/li>\n<\/ul>",
      "hascontent": 1,
      "anchor": "core_post"
    }
  }
]
```

---
`POST`
Query parameters:

```py
params = {
    "sesskey": "<sesskey>",
    "info": "core_tag_get_tagindex"
}
```

Request payload (JSON):

```py
payload_json = [{
    "index": 0,  # idk what this is
    "methodname": "core_tag_get_tagindex",
    "args": {
        "tagindex": {
            "tc": "1",  # idk what this is, comes with link to blog post as query param, doesn't seem to serve a purpose
            "tag": "<tag name>",
            "ta": "1",  # IMPORTANT, only change
            "page": "<page idx as string ig>"}
    }}]
```

example response:

```JSON
[
  {
    "error": false,
    "data": {
      "tagid": 643,
      "ta": 1,
      "component": "core",
      "itemtype": "user",
      "nextpageurl": null,
      "prevpageurl": "https:\/\/vle.kegs.org.uk\/tag\/index.php?tc=1&tag=Woodlouse&ta=1&page=0",
      "exclusiveurl": "https:\/\/vle.kegs.org.uk\/tag\/index.php?tc=1&tag=Woodlouse&ta=1&excl=1",
      "exclusivetext": "Show only tagged User interests",
      "title": "User interests",
      "content": "<ul class=\"tag_feed media-list\">\n        <li class=\"media\">\n                <div class=\"itemimage\">\n                    <a href=\"https:\/\/vle.kegs.org.uk\/user\/profile.php?id=3289\"><img src=\"https:\/\/vle.kegs.org.uk\/pluginfile.php\/22925\/user\/icon\/trema\/f2?rev=105591\" class=\"userpicture\" width=\"35\" height=\"35\" alt=\"Picture of Fraser Holmes\" title=\"Picture of Fraser Holmes\" \/><\/a>\n                <\/div>\n            <div class=\"media-body\">\n                    <div class=\"media-heading\">\n                        <a href=\"https:\/\/vle.kegs.org.uk\/user\/view.php?id=3289\">Fraser Holmes<\/a>\n                    <\/div>\n            <\/div>\n        <\/li>\n        <li class=\"media\">\n                <div class=\"itemimage\">\n                    <a href=\"https:\/\/vle.kegs.org.uk\/user\/profile.php?id=3355\"><img src=\"https:\/\/vle.kegs.org.uk\/pluginfile.php\/23983\/user\/icon\/trema\/f2?rev=105141\" class=\"userpicture\" width=\"35\" height=\"35\" alt=\"Cho Man\" title=\"Cho Man\" \/><\/a>\n                <\/div>\n            <div class=\"media-body\">\n                    <div class=\"media-heading\">\n                        <a href=\"https:\/\/vle.kegs.org.uk\/user\/view.php?id=3355\">Edward James<\/a>\n                    <\/div>\n            <\/div>\n        <\/li>\n        <li class=\"media\">\n                <div class=\"itemimage\">\n                    <a href=\"https:\/\/vle.kegs.org.uk\/user\/profile.php?id=4053\"><img src=\"https:\/\/vle.kegs.org.uk\/pluginfile.php\/37245\/user\/icon\/trema\/f2?rev=108545\" class=\"userpicture\" width=\"35\" height=\"35\" alt=\"Picture of Mario Feise\" title=\"Picture of Mario Feise\" \/><\/a>\n                <\/div>\n            <div class=\"media-body\">\n                    <div class=\"media-heading\">\n                        <a href=\"https:\/\/vle.kegs.org.uk\/user\/view.php?id=4053\">Mario Feise<\/a>\n                    <\/div>\n            <\/div>\n        <\/li>\n<\/ul>",
      "hascontent": 1,
      "anchor": "core_user"
    }
  }
]
```

This also lets you find out a tagid.

## https://vle.kegs.org.uk/tag/edit.php

`POST`
Edit a tag's page

request payload:

```py
payload = {
    "id": 643,
    "returnurl": None,
    "sesskey": "<sesskey>",
    "_qf__tag_edit_form": 1,
    "mform_isexpanded_id_tag": 1,
    "description_editor[text]": "<html description content>",
    "description_editor[format]": 1,
    "description_editor[itemid]": "Item id. probably in html somewhere",
    "relatedtags": "_qf__force_multiselect_submission",
    "relatedtags[]": ["<list of related tags>"],  # We can't have duplicate dict keys
    "submitbutton": "Update"
}
```

## https://vle.kegs.org.uk/tag/user.php

`GET`

Remove interest of a tag

query string parameters:

```py
params = {
    "action": "removeinterest",
    "sesskey": "<sesskey>",
    "tag": "<tag name>"
}
```

---
`GET`

Add interest of a tag

query string parameters:

```py
params = {
    "action": "addinterest",
    "sesskey": "<sesskey>",
    "tag": "<tag name>"
}
```

---
`GET`

Flag tag as inappropriate

```py
params = {
    "action": "flaginappropriate",
    "sesskey": "<sesskey>",
    "id": "<tag id>"
}
```

## https://vle.kegs.org.uk/tag/search.php

`GET`

HTML contains 150 most popular tags

---
`GET`

query params:

```py
params = {
    "query": "<search param>",
    "go": "Search"  # This doesn't seem to be a required param
}
```

will return some html

## https://vle.kegs.org.uk/lib/ajax/service.php?sesskey=H1tDtZ5sK2&info=core_calendar_submit_create_update_form

`POST`

Create a calander event
e
params:
```py
params = {
    "sesskey": ...,
    "info": "core_calendar_submit_create_update_form"
}
json = [
    {
        "index": 0, 
     "methodname": "core_calendar_submit_create_update_form",
        "args": {
            "formdata": """id=0
                        &userid=4053
                        &modulename=
                        &instance=0
                        &visible=1
                        &eventtype=user
                        &sesskey=H1tDtZ5sK2
                        &_qf__core_calendar_local_event_forms_create=1
                        &mform_showmore_id_general=1
                        &name=%3Cevent%20title%3E
                        &timestart%5Bday%5D=1
                        &timestart%5Bmonth%5D=1
                        &timestart%5Byear%5D=2025
                        &timestart%5Bhour%5D=9
                        &timestart%5Bminute%5D=47
                        &description%5Btext%5D=%3Ch1%3E%26lt%3Bevent%20description%26gt%3B%3C%2Fh1%3E%0D%0A%3Cp%3E%3Cem%3E%26lt%3Bsample%20text%26gt%3B%3C%2Fem%3E%3C%2Fp%3E
                        &description%5Bformat%5D=1
                        &description%5Bitemid%5D=188911336
                        &location=%3CLocation%3E
                        &duration=0"""
        }
    }
]

```