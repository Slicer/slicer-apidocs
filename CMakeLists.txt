cmake_minimum_required(VERSION 2.8)

###

get_filename_component(Slicer_SOURCE_DIR ${Slicer_SRC} ABSOLUTE)
get_filename_component(Slicer_BINARY_DIR ${DOC_OUT} ABSOLUTE)

###

set(PROJECT_NAME "Slicer")
set(SLICER_VERSION "4.7")
set(Slicer_VERSION_MAJOR "4")
set(Slicer_VERSION_MINOR "7")
set(Slicer_VERSION_PATCH "0")

###

add_custom_target(doc ${all_arg})
add_custom_target(doc-tarballs ${all_arg})
add_subdirectory(${Slicer_SOURCE_DIR}/Utilities/Doxygen)
