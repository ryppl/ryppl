get_property(ryppl_included GLOBAL PROPERTY RYPPL_INCLUDED DEFINED)
if(NOT ${ryppl_included})

  define_property(GLOBAL PROPERTY RYPPL_INCLUDED
    BRIEF_DOCS "Functions as an include() guard at the CMake level"
    FULL_DOCS "Prevents us from overriding the built-in find_package function twice"
    "See http://www.cmake.org/pipermail/cmake/2011-March/043320.html for more information"
    )

  include(CMakeParseArguments)

  function(find_package)
    get_directory_property(find_package_args RYPPL_FIND_PACKAGE_ARGS)

    if (find_package_args)
      set(find_package_args ${find_package_args} ";" ${ARGN})
    else()
      set(find_package_args ${ARGN})
    endif()

    set_property(DIRECTORY PROPERTY RYPPL_FIND_PACKAGE_ARGS ${find_package_args})
    message(STATUS "${PROJECT_NAME}.RYPPL_FIND_PACKAGE_ARGS: ${find_package_args}")
    _find_package(${ARGN})
  endfunction(find_package)
endif()
