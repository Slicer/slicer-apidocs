cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(SlicerDoxygenBuilder)

# Sanity checks
foreach(var IN ITEMS
  Slicer_VERSION
  Slicer_SOURCE_DIR
  )
  if(NOT DEFINED ${var})
    message(FATAL_ERROR "${var} is mandatory")
  endif()
endforeach()

find_package(Doxygen REQUIRED dot)

set(Slicer_BINARY_DIR ${CMAKE_BINARY_DIR})

###

set(PROJECT_NAME "Slicer")

###
add_custom_target(doc)
add_custom_target(doc-tarballs)
add_subdirectory(${Slicer_SOURCE_DIR}/Utilities/Doxygen Utilities/Doxygen)
