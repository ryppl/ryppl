################################################################################
# Copyright (C) 2012 Dave Abrahams <dave@boostpro.com>                         #
#                                                                              #
# Distributed under the Boost Software License, Version 1.0.                   #
# See accompanying file LICENSE_1_0.txt or copy at                             #
#   http://www.boost.org/LICENSE_1_0.txt                                       #
################################################################################
if(__RYPPL_FIND_PACKAGE_INCLUDED)
  return()
endif()
set(__RYPPL_FIND_PACKAGE_INCLUDED TRUE)

function(ryppl_do_find_package)
  string(REGEX REPLACE "\;" "\\\;" argument_pack "${ARGV}")
  if("${CMAKE_CURRENT_LIST_DIR}" STREQUAL "${PROJECT_SOURCE_DIR}")
    set_property(DIRECTORY APPEND PROPERTY RYPPL_FIND_PACKAGE_ARGS "${argument_pack}")
  endif()
  get_property(find_package_args GLOBAL PROPERTY ${PROJECT_NAME}_FIND_PACKAGE_ARGS)
  list(FIND find_package_args "${argument_pack}" index)
  if("${index}" EQUAL "-1")
    set_property(GLOBAL APPEND PROPERTY ${PROJECT_NAME}_FIND_PACKAGE_ARGS "${argument_pack}")
  endif()
endfunction(ryppl_do_find_package)

macro(ryppl_find_package)
  if(RYPPL_INITIAL_PASS)
    find_package(${ARGV} QUIET MODULE)
  else()
    find_package(${ARGV} REQUIRED)
  endif()
  ryppl_do_find_package(${ARGV})
endmacro(ryppl_find_package)
