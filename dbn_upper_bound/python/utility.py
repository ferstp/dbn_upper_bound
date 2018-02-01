"""
This module contains various math utilities for the main project
Most functions here are implementations of formulas derived in Terry's blogpost 
https://terrytao.wordpress.com/2018/01/27/polymath15-first-thread-computing-h_t-asymptotics-and-dynamics-of-zeroes/ [TT_Ht]

"""

from cmath import exp, log, cos, sqrt
from scipy.integrate import quad
from scipy.optimize import fsolve
import scipy
from dbn_upper_bound.python.constants import PI, PI_sq


def Nt(t, T):
    """
    Evaluates equation (4) in [TT_Ht]
    :param t: the "time" parameter
    :type t: float
    :param T: height
    :type T: float
    :return: right side of (4) in the blog link
    """
    T = float(T)
    T_by_4PI = T/(4*PI)

    return T_by_4PI*log(T_by_4PI) - T_by_4PI + (t/16.0)*log(T_by_4PI)


def phi_decay(u, n_max=100):
    """
    Phi function in the H_t integrand that decays rapidly with increasing n
    :param u:
    :type u:
    :param n_max:
    :type n_max: integer
    :return:
    """
    running_sum = 0
    for n in range(1, n_max+1):
        term1 = 2*PI_sq*pow(n, 4)*exp(9*u) - 3*PI*pow(n, 2)*exp(5*u)
        term2 = exp(-1*PI*pow(n, 2)*exp(4*u))
        running_sum += term1*term2

    return running_sum


def Ht_complex_integrand(u, z, t):
    """
    complex valued H_t integrand
    :param u:
    :type u:
    :param z:
    :type z:
    :param t:
    :type t:
    :return:
    """
    return exp(t*u*u)*phi_decay(u)*cos(z*u)


def Ht_complex(z, t):
    """
    complex valued H_t integral (refer to introductory section in [TT_Ht]
    :param z:
    :type z:
    :param t:
    :type t:
    :return:
    """
    #may work well only for small to medium values of z
    def real_func(a, b, c): return scipy.real(Ht_complex_integrand(a, b, c))
    def imag_func(a, b, c): return scipy.imag(Ht_complex_integrand(a, b, c))
    real_part = quad(real_func, 0, 10, args=(z, t))
    imag_part = quad(imag_func, 0, 10, args=(z, t))
    return (real_part[0] + 1j*imag_part[0], real_part[1], imag_part[1])


def Ht_complex_root_finding_helper(z_as_array, t):
    """
    Assistant function to the one below
    :param z_as_array:
    :type z_as_array:
    :param t:
    :type t:
    :return:
    """
    z = float(z_as_array[0]) + 1j*float(z_as_array[1])
    Ht = Ht_complex(z, t)[0]
    return (scipy.real(Ht), scipy.imag(Ht))


def Ht_complex_root_finder(complex_guess, t):
    """
    finds a complex valued root of H_t starting using a complex valued guess. Resulting imaginary parts expected to be just rounding errors.
    :param complex_guess:
    :param t:
    :return:
    """
    result = fsolve(Ht_complex_root_finding_helper,
                    [scipy.real(complex_guess), scipy.imag(complex_guess)],
                    args=(t,))
    return result[0]+1j*result[1]


def Ht_complex_zlarge(z, t):
    """
    Approx formula for Ht for large z values
    check last section of [TT_Ht]
    :param z:
    :param t:
    :return:
    """
    x = float(scipy.real(z))
    y = float(scipy.imag(z))
    t = float(t)
    x_by_4PI = x/(4*PI)
    B = ((PI*t/16)+(x/4))*log(x_by_4PI) - (x/4) + PI*(9+y)/8
    A1 = PI_sq*sqrt(PI/(2*1j*x))*pow(x_by_4PI, (9+y)/4)
    A2 = exp(-1*PI*x/8)
    A3 = exp((t/16)*pow(log(x_by_4PI), 2) - (t*PI_sq/64))
    Ht_without_PIby8_amplitude = A1*A3*exp(-1j*B)
    Ht = Ht_without_PIby8_amplitude*A2
    Ht_magnitude = abs(Ht)
    return (Ht, Ht_magnitude, Ht_without_PIby8_amplitude)


def Ht_real_integrand(u, z, t):
    """
    Real valued integrand for Ht
    :param u:
    :param z:
    :param t:
    :return:
    """
    if abs(scipy.imag(z)) > 0 or abs(scipy.imag(t)) > 0 \
            or abs(scipy.imag(u)) > 0:
        print("complex values not allowed for this function")
        return "error"

    u, z, t = scipy.real(u), scipy.real(z), scipy.real(t)
    return scipy.real(exp(t*u*u)*phi_decay(u)*cos(z*u))


def Ht_real(z, t):
    """
    Ht as a real valued integral
    :param z:
    :param t:
    :return:
    """
    if abs(scipy.imag(z)) > 0 or abs(scipy.imag(t)) > 0:
        print("complex values not allowed for this function")
        return "error"
    z, t = scipy.real(z), scipy.real(t)
    # return quad(Ht_real_integrand, 0, np.inf, args=(z,t))
    # causing overflow errors so np.inf replaced with 10
    return quad(Ht_real_integrand, 0, 10, args=(z, t))


def Ittheta_scaled_by_exp_z_pi_by_8(b,beta,t,theta=0):
    """
    refer to eqn (3) in [TT_Ht]
    eqn (3) scaled here by exp(pi*x/8) since the reciprocal is expected to the main decay term in Ittheta 
    :param b:
    :param beta:
    :param t:
    :param theta:
    :return:
    """
    def Ittheta_integrand_scaled_by_exp_z_pi_by_8(v,b,beta,t,theta):
        return exp(t*(v+1j*theta)*(v+1j*theta) - beta*exp(4*(v+1j*theta)) + 1j*b*(v+1j*theta)+ PI*scipy.real(b)/8)
    def real_func(a1,a2,a3,a4,a5): return scipy.real(Ittheta_integrand_scaled_by_exp_z_pi_by_8(a1,a2,a3,a4,a5))
    def imag_func(a1,a2,a3,a4,a5): return scipy.imag(Ittheta_integrand_scaled_by_exp_z_pi_by_8(a1,a2,a3,a4,a5))
    real_part = quad(real_func, 0, 10, args=(b,beta,t,theta))
    imag_part = quad(imag_func, 0, 10, args=(b,beta,t,theta))
    return real_part[0] + 1j*imag_part[0]


def Kttheta_scaled_by_exp_z_pi_by_8(z,t,n=5):
    """
    refer to section just prior to eqn (3) in [TT_Ht]
    Calculating Kttheta (scaled here by exp(pi*x/8))
    :param z:
    :param t:
    :param n:
    :return:
    """
    theta = PI/8 - 1/(4*scipy.real(z))
    running_sum=0
    for n in range(1,5):
        running_sum += 2*PI_sq*n*n*n*n*Ittheta_scaled_by_exp_z_pi_by_8(z-9j,PI*n*n,t,theta) - 3*PI*n*n*Ittheta_scaled_by_exp_z_pi_by_8(z-5j,PI*n*n,t,theta)
    return running_sum


def Ht_large_scaled_by_exp_z_pi_by_8(z,t):
    """
    refer to eqn (2) in [TT_Ht]
    Calculating Ht (scaled here by exp(pi*x/8)), with hopefully good behavior for larger z values
    :param z:
    :param t:
    :return:
    """
    return 0.5*(Kttheta_scaled_by_exp_z_pi_by_8(z,t) + Kttheta_scaled_by_exp_z_pi_by_8(z.conjugate(),t).conjugate()) 


def Ht_large_root_finding_helper(z_as_array,t):
    """
    Assistant function to the one below
    :param z_as_array:
    :param t:
    :return:
    """
    z = float(z_as_array[0]) + 1j*float(z_as_array[1])
    val = Ht_large_scaled_by_exp_z_pi_by_8(z,t)
    return (scipy.real(val),scipy.imag(val))


def Ht_large_root_finder(complex_guess,t):
    """
    Ht root finding using Ht_large_scaled_by_exp_z_pi_by_8(z,t)
    :param complex_guess:
    :param t:
    :return:
    """
    result = fsolve(Ht_large_root_finding_helper,[scipy.real(complex_guess),scipy.imag(complex_guess)],args=(t,))
    return result[0]+1j*result[1]


#check phi_decay values
'''print(phi_decay(0.001))
print(phi_decay(0.01))
print(phi_decay(0.1))
print(phi_decay(0.5))
print(phi_decay(1))'''
