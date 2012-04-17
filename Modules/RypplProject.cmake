################################################################################
# Copyright (C) 2012 Dave Abrahams <dave@boostpro.com>                         #
#                                                                              #
# Distributed under the Boost Software License, Version 1.0.                   #
# See accompanying file LICENSE_1_0.txt or copy at                             #
#   http://www.boost.org/LICENSE_1_0.txt                                       #
################################################################################

if(__RypplProject_INCLUDED)
  return()
endif()
set(__RypplProject_INCLUDED True)

include(CMakeParseArguments)

function(ryppl_project_
    name   # a short name to identify the interface (e.g. "Foo")
    )
  set(options
    NEEDS_TERMINAL
    # if present, this element indicates that the program requires a
    # terminal in order to run. Graphical launchers should therefore
    # run this program in a suitable terminal emulator.

    HEADER_ONLY
    # This option is equivalent to passing NONE as a LANGUAGES
    # argument (see below)
    )

  set(one_value_keywords
    FEED_URI
    # This attribute is only needed for remote feeds (fetched via
    # HTTP). The value must exactly match the expected URL, to
    # prevent an attacker replacing one correctly-signed feed with
    # another (e.g., returning a feed for the shred program when the
    # user asked for the backup program).

    SUMMARY
    # a short one-line description; the first word should not be
    # upper-case unless it is a proper noun (e.g. "cures all ills")

    DESCRIPTION
    # a full description, which can be several paragraphs long
    # (optional since 0.32, but recommended)

    HOMEPAGE
    # the URL of a web-page describing this interface in more detail

    FEED
    # the linked feed contains more implementations of this feed's
    # interface. The "langs" and "arch" attributes, if present,
    # indicate that all implementations will fall within these
    # limits (e.g. arch='*-src' means that there is no point
    # fetching this feed unless you are looking for source code).
    # See the <implementation> element for a description of the
    # values of these attributes.

    FEED_FOR
    # the implementations in this feed are implementations of the
    # given interface. This is used when adding a third-party feed.

    REPLACED_BY
    # this feed's interface (the one in the root element's uri
    # attribute) has been replaced by the given interface. Any
    # references to the old URI should be updated to use the new
    # one.

    )

  set(multi_value_keywords
    CATEGORY
    # a classification for the interface. If no type is given, then
    # the category is one of the 'Main' categories defined by the
    # freedesktop.org menu specification. Otherwise, it is a URI
    # giving the namespace for the category.

    ICON
    # an icon to use for the program; this is used by programs such
    # as AddApp.

    CMAKE_LANGUAGES

    KEYWORDS
    # A list of additional keywords to be used to assist searching for the distribution in a larger catalog
    AUTHOR
    # The primary author(s) of the program. (dc:creator)
    MAINTAINER
    # The primary maintainer(s) of the program. (dc:publisher)
    )

  cmake_parse_arguments(RYPPL_PROJECT "${options}" "${one_value_keywords}" "${multi_value_keywords}" ${ARGN})
  foreach(name ${options} ${one_value_keywords} ${multi_value_keywords})
    set_property(DIRECTORY PROPERTY RYPPL_PROJECT_${name} ${RYPPL_PROJECT_${name}})
  endforeach()
  if(RYPPL_PROJECT_UNPARSED_ARGUMENTS)
    message(FATAL_ERROR "Unknown keywords given to ryppl_project(): \"${RYPPL_PROJECT_UNPARSED_ARGUMENTS}\"")
  endif()
endfunction(ryppl_project_)

macro(ryppl_project projectname)
  cmake_parse_arguments(RYPPL_PROJECT "" "" "CMAKE_LANGUAGES" ${ARGN})
  project(${projectname} ${RYPPL_PROJECT_CMAKE_LANGUAGES})
  ryppl_project_(${ARGV})
endmacro(ryppl_project)
