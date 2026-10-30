submodule (shapes:z_parent) a_child
  implicit none
contains
  module procedure perimeter
    p = 2*pi*r
  end procedure perimeter
end submodule a_child
