module area
  use consts, only: dp, pi
  implicit none
contains
  pure function circle(r) result(a)
    real(dp), intent(in) :: r
    real(dp) :: a
    a = pi*r**2
  end function circle
end module area
