#=============================================================================
# Copyright (C) 2012 Daniel Pfeifer <daniel@pfeifer-mail.de>
#
# Distributed under the Boost Software License, Version 1.0.
# See accompanying file LICENSE_1_0.txt or copy at
#   http://www.boost.org/LICENSE_1_0.txt
#=============================================================================

cmake_minimum_required(VERSION 2.8.10 FATAL_ERROR)
project(Ryppl NONE)

set(CMAKE_MODULE_PATH "${Ryppl_SOURCE_DIR}/cmake/Modules")

include(RypplDocumentation)

file(GLOB modules "cmake/Modules/*.cmake")

set(cmake_docbook "${CMAKE_BINARY_DIR}/cmake.docbook")
add_custom_command(OUTPUT ${cmake_docbook}
  COMMAND ${CMAKE_COMMAND}
    -DCMAKE_MODULE_PATH="${CMAKE_MODULE_PATH}"
    --help-full ${cmake_docbook}
  DEPENDS ${modules}
  )
ryppl_documentation(${cmake_docbook})

