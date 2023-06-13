"""
Molecular integrals over Gaussian basis functions generated by sympleints.
See https://github.com/eljost/sympleints for more information.

sympleints version: 0.1.dev79+g63f1ef8.d20230515
symppy version: 1.10.1

sympleints was executed with the following arguments:
	lmax = 4
	lauxmax = 6
	write = False
	out_dir = devel_ints
	keys = ['~2c2e', '~3c2e_sph']
	sph = False
	opt_basic = True
	normalize = cgto
"""

import numpy


def cart_gto3d_0(ax, da, A, R):
    """3D Cartesian s-Gaussian shell.
    Exponent ax, contraction coeff. da, centered at A, evaluated at R.

    Generated code; DO NOT modify by hand!"""

    result = numpy.zeros((1,), dtype=float)

    # 1 item(s)
    result[0] = numpy.sum(
        da
        * numpy.exp(-ax * ((A[0] - R[0]) ** 2 + (A[1] - R[1]) ** 2 + (A[2] - R[2]) ** 2))
    )
    return result


def cart_gto3d_1(ax, da, A, R):
    """3D Cartesian p-Gaussian shell.
    Exponent ax, contraction coeff. da, centered at A, evaluated at R.

    Generated code; DO NOT modify by hand!"""

    result = numpy.zeros((3,), dtype=float)

    x0 = A[0] - R[0]
    x1 = A[1] - R[1]
    x2 = A[2] - R[2]
    x3 = da * numpy.exp(-ax * (x0**2 + x1**2 + x2**2))

    # 3 item(s)
    result[0] = numpy.sum(-x0 * x3)
    result[1] = numpy.sum(-x1 * x3)
    result[2] = numpy.sum(-x2 * x3)
    return result


def cart_gto3d_2(ax, da, A, R):
    """3D Cartesian d-Gaussian shell.
    Exponent ax, contraction coeff. da, centered at A, evaluated at R.

    Generated code; DO NOT modify by hand!"""

    result = numpy.zeros((6,), dtype=float)

    x0 = A[0] - R[0]
    x1 = x0**2
    x2 = A[1] - R[1]
    x3 = x2**2
    x4 = A[2] - R[2]
    x5 = x4**2
    x6 = da * numpy.exp(-ax * (x1 + x3 + x5))
    x7 = 0.5773502691896258 * x6
    x8 = x0 * x6

    # 6 item(s)
    result[0] = numpy.sum(x1 * x7)
    result[1] = numpy.sum(x2 * x8)
    result[2] = numpy.sum(x4 * x8)
    result[3] = numpy.sum(x3 * x7)
    result[4] = numpy.sum(x2 * x4 * x6)
    result[5] = numpy.sum(x5 * x7)
    return result


def cart_gto3d_3(ax, da, A, R):
    """3D Cartesian f-Gaussian shell.
    Exponent ax, contraction coeff. da, centered at A, evaluated at R.

    Generated code; DO NOT modify by hand!"""

    result = numpy.zeros((10,), dtype=float)

    x0 = A[0] - R[0]
    x1 = x0**2
    x2 = A[1] - R[1]
    x3 = x2**2
    x4 = A[2] - R[2]
    x5 = x4**2
    x6 = da * numpy.exp(-ax * (x1 + x3 + x5))
    x7 = 0.2581988897471611 * x6
    x8 = x2 * x6
    x9 = 0.5773502691896258
    x10 = x1 * x9
    x11 = x4 * x6
    x12 = x3 * x9
    x13 = x0 * x6
    x14 = x5 * x9

    # 10 item(s)
    result[0] = numpy.sum(-(x0**3) * x7)
    result[1] = numpy.sum(-x10 * x8)
    result[2] = numpy.sum(-x10 * x11)
    result[3] = numpy.sum(-x12 * x13)
    result[4] = numpy.sum(-x0 * x4 * x8)
    result[5] = numpy.sum(-x13 * x14)
    result[6] = numpy.sum(-(x2**3) * x7)
    result[7] = numpy.sum(-x11 * x12)
    result[8] = numpy.sum(-x14 * x8)
    result[9] = numpy.sum(-(x4**3) * x7)
    return result


def cart_gto3d_4(ax, da, A, R):
    """3D Cartesian g-Gaussian shell.
    Exponent ax, contraction coeff. da, centered at A, evaluated at R.

    Generated code; DO NOT modify by hand!"""

    result = numpy.zeros((15,), dtype=float)

    x0 = -A[0] + R[0]
    x1 = x0**2
    x2 = -A[1] + R[1]
    x3 = x2**2
    x4 = -A[2] + R[2]
    x5 = x4**2
    x6 = da * numpy.exp(-ax * (x1 + x3 + x5))
    x7 = 0.09759000729485332 * x6
    x8 = 0.2581988897471611 * x6
    x9 = x0**3 * x8
    x10 = 0.3333333333333333 * x6
    x11 = x1 * x10
    x12 = 1.732050807568877
    x13 = x12 * x4
    x14 = x2**3
    x15 = x0 * x8
    x16 = x10 * x3
    x17 = x4**3

    # 15 item(s)
    result[0] = numpy.sum(x0**4 * x7)
    result[1] = numpy.sum(x2 * x9)
    result[2] = numpy.sum(x4 * x9)
    result[3] = numpy.sum(x11 * x3)
    result[4] = numpy.sum(x11 * x13 * x2)
    result[5] = numpy.sum(x11 * x5)
    result[6] = numpy.sum(x14 * x15)
    result[7] = numpy.sum(x0 * x13 * x16)
    result[8] = numpy.sum(x0 * x10 * x12 * x2 * x5)
    result[9] = numpy.sum(x15 * x17)
    result[10] = numpy.sum(x2**4 * x7)
    result[11] = numpy.sum(x14 * x4 * x8)
    result[12] = numpy.sum(x16 * x5)
    result[13] = numpy.sum(x17 * x2 * x8)
    result[14] = numpy.sum(x4**4 * x7)
    return result


cart_gto3d = {
    (0,): cart_gto3d_0,
    (1,): cart_gto3d_1,
    (2,): cart_gto3d_2,
    (3,): cart_gto3d_3,
    (4,): cart_gto3d_4,
}