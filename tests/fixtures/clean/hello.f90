program hello
  use, intrinsic :: iso_fortran_env, only: dp => real64
  implicit none
  real(dp) :: x
  x = 1.0_dp
  print *, x
end program hello
