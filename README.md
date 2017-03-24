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
usage: slicer-apidocs-builder [-h] [--repo REPO] [--branch BRANCH] [--tag TAG]
                              [--slicer-src-dir SLICER_SRC_DIR]
                              [--publish-github-repo PUBLISH_GITHUB_REPO]
                              [--publish-github-branch PUBLISH_GITHUB_BRANCH]
                              [--publish-github-token PUBLISH_GITHUB_TOKEN]
                              [--skip-build]

optional arguments:
  -h, --help            show this help message and exit
  --repo REPO           Slicer repository to document (default: Slicer/Slicer)
  --branch BRANCH       Slicer branch to document (default: master)
  --tag TAG             Slicer tag to document. If specified --branch is
                        ignored.
  --slicer-src-dir SLICER_SRC_DIR
                        Slicer sources checkout to reuse. By default, checkout
                        source in TEMP directory.
  --publish-github-repo PUBLISH_GITHUB_REPO
                        Github repository hosting generated HTML documentation
                        (default: slicer/apidocs.slicer.org)
  --publish-github-branch PUBLISH_GITHUB_BRANCH
                        Github branch hosting generated HTML documentation
                        (default: gh-pages)
  --publish-github-token PUBLISH_GITHUB_TOKEN
                        GitHub Token allowing to publish generated
                        documentation (default: GITHUB_TOKEN env. variable)
  --skip-build          If specified, skip generation of HTML and reuse
                        existing files.
```


# license

It is covered by the Slicer License:

https://github.com/slicer-apidocs-builder/License.txt


