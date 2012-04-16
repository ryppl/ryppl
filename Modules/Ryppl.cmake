if(__RYPPL_INCLUDED)
  return()
endif()
set(__RYPPL_INCLUDED TRUE)

function(find_package)
  _find_package(${ARGV})

  get_cmake_property(variables VARIABLES)
  foreach(variable ${variables})
    set(${variable} ${${variable}} PARENT_SCOPE)
  endforeach()

  get_directory_property(find_package_args RYPPL_FIND_PACKAGE_ARGS)

  if (find_package_args)
    set(find_package_args ${find_package_args} ";" ${ARGV})
  else()
    set(find_package_args ${ARGN})
  endif()
endfunction(find_package)


