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

## master

API documentation associated with the [Slicer/Slicer@master](https://github.com/Slicer/Slicer/tree/master)
branch is available under the `master` subpage.

The `master` subpage is automatically updated each time the corresponding GitHub branch is updated.

## pull requests

API documentation associated with a pull request is available under a subpage named after the pull request
branch.

# usage

```bash
usage: slicer-apidocs-builder [-h] [--slicer-repo-name SLICER_REPO_NAME]
                              [--slicer-repo-dir SLICER_REPO_DIR]
                              [--slicer-repo-branch SLICER_REPO_BRANCH]
                              [--slicer-repo-tag SLICER_REPO_TAG]
                              [--skip-build]
                              [--publish-github-username PUBLISH_GITHUB_USERNAME]
                              [--publish-github-useremail PUBLISH_GITHUB_USEREMAIL]
                              [--publish-github-repo-name PUBLISH_GITHUB_REPO_NAME]
                              [--publish-github-repo-branch PUBLISH_GITHUB_REPO_BRANCH]
                              [--publish-github-token PUBLISH_GITHUB_TOKEN]

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
                        Slicer branch to document (default: master)
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
```


# license

It is covered by the Slicer License:

https://github.com/slicer-apidocs-builder/License.txt


