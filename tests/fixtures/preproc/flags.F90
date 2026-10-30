program flags
  implicit none
#ifdef USE_FAST
  integer :: mode = 1
#else
  integer :: mode = 2
#endif
  print *, mode
end program flags
