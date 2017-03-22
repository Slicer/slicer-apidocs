#!/bin/bash

set -e
set -o pipefail
set -x

if [ $TRAVIS ]; then
    git config --global push.default simple
    git config --global user.name "Slicer Dox CI"
    git config --global user.email "none@users.noreply.github.com"
fi

if [ ! -d "build/slicer-src/.git" ]; then
    git clone --depth=1 https://github.com/Slicer/slicer build/slicer-src;
fi;

mkdir -p build/dox
cd build/dox

if [ ! -d "Utilities/Doxygen" ]; then
      mkdir -p Utilities/Doxygen
fi

cmake -DSlicer_SRC=build/slicer-src -DDOC_OUT=build/dox ../../

make doc

cd Utilities/Doxygen/html/

git init
git checkout --orphan gh-pages || true
git add --all
git commit -m "$PROJECT Doxygen pages update $DATE" # todo

######## important: don't echo token
set +x
git push --force "https://${GH_REPO_TOKEN}@github.com/ihnorton/slicerapi" gh-pages > /dev/null 2>&1
########
