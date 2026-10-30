program app
  use lib, only: scale
  implicit none
  real :: x = 1.0
  call scale(x)
  print *, x
end program app
