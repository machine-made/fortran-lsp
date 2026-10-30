submodule (shapes) z_parent
  implicit none
  real, parameter :: pi = 3.14159265
contains
  module procedure area
    a = pi*r**2
  end procedure area
end submodule z_parent
