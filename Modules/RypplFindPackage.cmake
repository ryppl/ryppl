################################################################################
# Copyright (C) 2012 Dave Abrahams <dave@boostpro.com>                         #
#                                                                              #
# Distributed under the Boost Software License, Version 1.0.                   #
# See accompanying file LICENSE_1_0.txt or copy at                             #
#   http://www.boost.org/LICENSE_1_0.txt                                       #
################################################################################

include(CMakeParseArguments)

function(ryppl_find_package)
  cmake_parse_arguments(FIND_PACKAGE "EXACT QUIET NO_POLICY_SCOPE" "" "REQUIRED COMPONENTS" ${ARGN})
  find_package(${ARGN})
endfunction(ryppl_find_package)



