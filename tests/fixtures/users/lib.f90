module lib
  implicit none
contains
  subroutine scale(x, factor)
    real, intent(inout) :: x
    real, intent(in) :: factor
    x = x*factor
  end subroutine scale
end module lib
