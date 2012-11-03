# This function creates a suite of regression tests.
#
#   ryppl_test_suite([name]
#     [COMPILE        <list of source files>]
#     [COMPILE_FAIL   <list of source files>]
#     [LINK           <list of source files>]
#     [LINK_FAIL      <list of source files>]
#     [MODULE_FAIL    <list of source files>]
#     [LINK_FAIL      <list of source files>]
#     [RUN            <list of source files>]
#     [RUN_FAIL       <list of source files>]
#     [PYTHON         <list of source files>]
#     [PYTHON_FAIL    <list of source files>]
#     [LINK_LIBRARIES <list of libraries to link>]
#     [NO_SINGLE_TARGET (deprecated!)]
#     )

#=============================================================================
# Copyright (C) 2012 Daniel Pfeifer <daniel@pfeifer-mail.de>
#
# Distributed under the Boost Software License, Version 1.0.
# See accompanying file LICENSE_1_0.txt or copy at
#   http://www.boost.org/LICENSE_1_0.txt
#=============================================================================

include(CMakeParseArguments)
include(detail/test_implementation)

if(NOT TARGET test)
  add_custom_target(test)
endif()  

function(ryppl_test_suite)
  if(RYPPL_DISABLE_TESTS)
    return()
  endif()

  set(args
    COMPILE
    COMPILE_FAIL
    LINK
    LINK_FAIL
    MODULE
    MODULE_FAIL
    RUN
    RUN_FAIL
    PYTHON
    PYTHON_FAIL
    ADDITIONAL_SOURCES
    LINK_LIBRARIES
    )

  cmake_parse_arguments(TEST "NO_SINGLE_TARGET" "" "${args}" ${ARGN})

  if("${PROJECT_NAME}" STREQUAL "${CMAKE_PROJECT_NAME}")
    set(target test)
  else()
    string(TOLOWER "${PROJECT_NAME}-test" target)
  endif()

  if(TARGET ${target})
    set(suffix 2)
    while(TARGET ${target}${suffix})
      math(EXPR suffix "${suffix} + 1")
    endwhile()
    set(target ${target}${suffix})
  endif()

  set(driver ${target}driver)
  set(TEST_FILES)

  # COMPILE tests
  foreach(FILE ${TEST_COMPILE})
    __boost_add_test_compile(0)
  endforeach()
  foreach(FILE ${TEST_COMPILE_FAIL})
    __boost_add_test_compile(1)
  endforeach()

  # LINK tests
  foreach(FILE ${TEST_LINK})
    __boost_add_test_link("${CMAKE_CXX_LINK_EXECUTABLE}" 0)
  endforeach()
  foreach(FILE ${TEST_LINK_FAIL})
    __boost_add_test_link("${CMAKE_CXX_LINK_EXECUTABLE}" 1)
  endforeach()

  # MODULE tests
  foreach(FILE ${TEST_MODULE})
    __boost_add_test_link("${CMAKE_CXX_CREATE_SHARED_MODULE}" 0)
  endforeach()
  foreach(FILE ${TEST_MODULE_FAIL})
    __boost_add_test_link("${CMAKE_CXX_CREATE_SHARED_MODULE}" 1)
  endforeach()

  # RUN tests
  if(NOT TEST_NO_SINGLE_TARGET AND (TEST_RUN OR TEST_RUN_FAIL))
    set(run_sources
      ${TEST_RUN}
      ${TEST_RUN_FAIL}
      )
    list(LENGTH run_sources length)
    if(length GREATER 1)
      foreach(file ${run_sources})
        get_filename_component(name "${file}" NAME_WE)
        set_property(SOURCE "${file}" APPEND PROPERTY
          COMPILE_DEFINITIONS "main=${name}"
          )
      endforeach()
      create_test_sourcelist(run_sources ${driver}.cpp ${run_sources})
    endif()
    add_executable(${driver} EXCLUDE_FROM_ALL
      ${run_sources}
      ${TEST_ADDITIONAL_SOURCES}
      )
    target_link_libraries(${driver}
      ${TEST_LINK_LIBRARIES}
      )
    foreach(FILE ${TEST_RUN})
      __boost_add_test_run(${driver} 0)
    endforeach()
    foreach(FILE ${TEST_RUN_FAIL})
      __boost_add_test_run(${driver} 1)
    endforeach()
  endif()

  # deprecated RUN tests
  if(TEST_NO_SINGLE_TARGET AND (TEST_RUN OR TEST_RUN_FAIL))
    set(SUFFIX 0)
    foreach(FILE ${TEST_RUN})
      __boost_add_test_run_deprecated(${driver} 0)
    endforeach()
    foreach(FILE ${TEST_RUN_FAIL})
      __boost_add_test_run_deprecated(${driver} 1)
    endforeach()
  endif()

  # PYTHON tests
  foreach(FILE ${TEST_PYTHON})
    __boost_add_test_python(0)
  endforeach()
  foreach(FILE ${TEST_PYTHON_FAIL})
    __boost_add_test_python(1)
  endforeach()

  # add the actual test target
  string(REPLACE ";" " " TEST_NAMES "${TEST_NAMES}")
  add_custom_target(${target}
    COMMAND ${CMAKE_COMMAND}
      -D "TESTS=${TEST_NAMES}"
      -P "${__boost_test_summary}"
    DEPENDS ${TEST_FILES}
    )
  add_dependencies(test ${target})
endfunction()
