# Slicer API documentation builder

This project allows to generate and publish the Slicer API documentation. See http://apidocs.slicer.org.

# builder script

The ``publish_apidocs.py`` script has 3 main steps:

* checkout Slicer source code
* build doxygen documentation
* publish generated html pages into [Slicer/apidocs.slicer.org@apidocs](https://github.com/Slicer/apidocs.slicer.org) branch.

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


# license

It is covered by the Slicer License:

https://github.com/slicer-apidocs-builder/License.txt


