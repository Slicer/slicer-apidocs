# Slicer API documentation builder

This project allows to generate and publish the Slicer API documentation. See http://apidocs.slicer.org.

# builder cli

The ``slicer-apidocs-builder`` cli has 3 main steps:

* checkout Slicer source code
* build doxygen documentation
* publish generated html pages into [Slicer/apidocs.slicer.org@gh-pages](https://github.com/Slicer/apidocs.slicer.org) branch.

# supported cases

## release

API documentation associated with each Slicer version is available under a `vX.Y` subpage
where X and Y respectively correspond to Slicer major and minor version.

A new subpage is automatically created after each release.

## main

API documentation associated with the [Slicer/Slicer@main](https://github.com/Slicer/Slicer/tree/main)
branch is available under the `main` subpage.

The `main` subpage is automatically updated each time the corresponding GitHub branch is updated.

## pull requests

API documentation associated with a pull request is available under a subpage named after the pull request
branch.

# usage

```
$ slicer-apidocs-builder --help
usage: slicer-apidocs-builder [-h] [--slicer-repo-name SLICER_REPO_NAME]
                              [--slicer-repo-dir SLICER_REPO_DIR]
                              [--slicer-repo-branch SLICER_REPO_BRANCH]
                              [--slicer-repo-tag SLICER_REPO_TAG]
                              [--skip-build]
                              [--publish-github-username PUBLISH_GITHUB_USERNAME]
                              [--publish-github-useremail PUBLISH_GITHUB_USEREMAIL]
                              [--publish-github-repo-dir PUBLISH_GITHUB_REPO_DIR]
                              [--publish-github-repo-name PUBLISH_GITHUB_REPO_NAME]
                              [--publish-github-repo-branch PUBLISH_GITHUB_REPO_BRANCH]
                              [--publish-github-token PUBLISH_GITHUB_TOKEN]
                              [--publish-github-skip-auth]
                              [--skip-publish]
                              [--status-update-state {pending,failure,success}]
                              [--status-update-target-url STATUS_UPDATE_TARGET_URL]
                              [--status-update-target-url-path STATUS_UPDATE_TARGET_URL_PATH]
                              [--status-update-revision STATUS_UPDATE_REVISION]
                              [--status-update-repo-name STATUS_UPDATE_REPO_NAME]
                              [--status-update-token STATUS_UPDATE_TOKEN]

optional arguments:
  -h, --help            show this help message and exit

Apidocs Building:
  --slicer-repo-name SLICER_REPO_NAME
                        Slicer repository to document (default:
                        Slicer/Slicer).
  --slicer-repo-dir SLICER_REPO_DIR
                        Slicer sources checkout to reuse. By default, checkout
                        source in TEMP directory.
  --slicer-repo-branch SLICER_REPO_BRANCH
                        Slicer branch to document (example: master)
  --slicer-repo-tag SLICER_REPO_TAG
                        Slicer tag to document. If specified --branch is
                        ignored.
  --skip-build          If specified, skip generation of HTML and reuse
                        existing files.

Apidocs Publishing:
  --publish-github-username PUBLISH_GITHUB_USERNAME
                        Github name to associate with the commits (default:
                        Slicer Bot)
  --publish-github-useremail PUBLISH_GITHUB_USEREMAIL
                        Github email to associate with the commits (default:
                        slicerbot@slicer.org)
  --publish-github-repo-dir PUBLISH_GITHUB_REPO_DIR
                        Existing checkout of repository hosting generated HTML documentation.
                        (default: automatically cloned based on --publish-github-repo-name)
  --publish-github-repo-name PUBLISH_GITHUB_REPO_NAME
                        Github repository hosting generated HTML documentation
                        (default: slicer/apidocs.slicer.org)
  --publish-github-repo-branch PUBLISH_GITHUB_REPO_BRANCH
                        Github branch hosting generated HTML documentation
                        (default: gh-pages)
  --publish-github-token PUBLISH_GITHUB_TOKEN
                        GitHub Token allowing to publish generated
                        documentation (default: PUBLISH_GITHUB_TOKEN env.
                        variable)
  --publish-github-skip-auth
                        If specified, attempt to publish without token.
  --skip-publish        If specified, skip publication of HTML files.

Apidocs Status Update:
  --status-update-state {pending,failure,success}
                        State of the apidocs
  --status-update-target-url STATUS_UPDATE_TARGET_URL
                        URL to associate with the state update. (default:
                        http://apidocs.slicer.org)
  --status-update-target-url-path STATUS_UPDATE_TARGET_URL_PATH
                        Path appended to target base URL.(default: based on
                        value of --slicer-repo-branch and --slicer-repo-tag)
  --status-update-revision STATUS_UPDATE_REVISION
                        Slicer revision to update(default to HEAD of Slicer
                        source checkout. See --slicer-repo-dir)
  --status-update-repo-name STATUS_UPDATE_REPO_NAME
                        Slicer repo name to update (default to --slicer-repo-
                        name)
  --status-update-token STATUS_UPDATE_TOKEN
                        GitHub token allowing to update status (default:
                        STATUS_UPDATE_GITHUB_TOKEN env. variable)
```


# license

It is covered by the Slicer License:

https://github.com/Slicer/slicer-apidocs-builder/blob/master/License.txt


