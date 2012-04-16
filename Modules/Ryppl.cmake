if(__RYPPL_INCLUDED)
  return()
endif()
set(__RYPPL_INCLUDED TRUE)

# Causes the built-in find_package to be renamed _find_package
function(find_package)
endfunction(find_package)

function(ryppl_find_package)
  get_directory_property(find_package_args RYPPL_FIND_PACKAGE_ARGS)

  if (find_package_args)
    set(find_package_args ${find_package_args} ";" ${ARGN})
  else()
    set(find_package_args ${ARGN})
  endif()

  set_property(DIRECTORY PROPERTY RYPPL_FIND_PACKAGE_ARGS ${find_package_args})
  message(STATUS "${PROJECT_NAME}.RYPPL_FIND_PACKAGE_ARGS: ${find_package_args}")
endfunction(ryppl_find_package)

macro(find_package)
  ryppl_find_package(${ARGV})
  _find_package(${ARGV})
endmacro(find_package)
