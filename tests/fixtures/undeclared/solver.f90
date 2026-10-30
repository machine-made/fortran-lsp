module solver
  implicit none
contains
  subroutine step(x)
    real, intent(inout) :: x
    y = x + 1.0
    x = y
  end subroutine step
end module solver
