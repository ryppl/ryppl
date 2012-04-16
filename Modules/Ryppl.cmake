if(__RYPPL_INCLUDED)
  return()
endif()
set(__RYPPL_INCLUDED TRUE)

function(ryppl_do_find_package)
  set_property(DIRECTORY APPEND PROPERTY RYPPL_FIND_PACKAGE_ARGS "${ARGV}")
endfunction(ryppl_do_find_package)

macro(ryppl_find_package)
  find_package(${ARGV})
  ryppl_do_find_package(${ARGV})
endmacro(ryppl_find_package)


