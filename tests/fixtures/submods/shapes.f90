module shapes
  implicit none
  interface
    module function area(r) result(a)
      real, intent(in) :: r
      real :: a
    end function area
    module function perimeter(r) result(p)
      real, intent(in) :: r
      real :: p
    end function perimeter
  end interface
end module shapes
