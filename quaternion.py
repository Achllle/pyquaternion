# A python module for basic quaternion math

# Add compatibility for Python 2x
from __future__ import absolute_import, division, print_function

import numpy as np
import random
from math import sqrt, pi, sin, cos, asin, acos, atan2

class Quaternion:

    def __init__(self, *args, **kwargs):
        s = len(args)
        if s is 0:
            # No positional arguments supplied
            if len(kwargs) > 0:
                # Keyword arguments provided
                if ("scalar" in kwargs) or ("vector" in kwargs):
                    scalar = kwargs.get("scalar", 0.0)
                    if scalar is None:
                        scalar = 0.0
                    else:
                        scalar = float(scalar)

                    vector = kwargs.get("vector", [])   
                    vector = self._validate_number_sequence(vector, 3)

                    self.q = np.hstack((scalar, vector)) 
                elif ("real" in kwargs) or ("imaginary" in kwargs):
                    real = kwargs.get("real", 0.0)
                    if real is None:
                        real = 0.0
                    else:
                        real = float(real)

                    imaginary = kwargs.get("imaginary", [])   
                    imaginary = self._validate_number_sequence(imaginary, 3)

                    self.q = np.hstack((real, imaginary))
                elif ("axis" in kwargs) or ("angle" in kwargs):
                    try:
                        axis = self._validate_number_sequence(kwargs["axis"], 3)
                        angle = float(kwargs["angle"])
                    except KeyError:
                        raise ValueError("Both 'axis' and 'angle' must be provided to describe a meaningful rotation.")
                    else:
                        self.q = Quaternion._from_axis_angle(axis, angle).q
                elif "array" in kwargs:
                    self.q = self._validate_number_sequence(kwargs["array"], 4)
                elif "matrix" in kwargs:
                    self.q = Quaternion._from_matrix(kwargs["matrix"]).q
                else:
                    keys = sorted(kwargs.keys())
                    elements = [kwargs[kw] for kw in keys]
                    if len(elements) is 1:
                        r = float(elements[0])
                        self.q = np.array([r, 0.0, 0.0, 0.0])
                    else:
                        self.q = self._validate_number_sequence(elements, 4)

            else: 
                # Default initialisation
                self.q = np.array([1.0, 0.0, 0.0, 0.0])
        elif s is 1:
            # Single positional argument supplied
            if isinstance(args[0], self.__class__):
                self.q = args[0].q
                return
            if args[0] is None:
                raise TypeError("Object cannot be initialised from " + str(type(args[0])))
            try:
                r = float(args[0])
                self.q = np.array([r, 0.0, 0.0, 0.0])
                return
            except(TypeError):
                pass # If the single argument is not scalar, it should be a sequence

            self.q = self._validate_number_sequence(args[0], 4)
            return
        
        else: 
            # More than one positional argument supplied
            self.q = self._validate_number_sequence(args, 4)

    def _validate_number_sequence(self, seq, n):
        if seq is None:
            return np.zeros(n)
        if len(seq) is n:
            try:
                l = [float(e) for e in seq]
            except ValueError:
                raise ValueError("One or more elements in sequence <" + str(seq) + "> cannot be interpreted as a real number")
            else:
                return np.asarray(l)
        elif len(seq) is 0:
            return np.zeros(n)
        else:
            raise ValueError("Unexpected number of elements in sequence.")

    # Initialise from matrix
    @classmethod
    def _from_matrix(cls, matrix):
        """ Create a Quaternion by specifying the 3x3 rotation or 4x4 transformation matrix 
        (as a numpy array) from which the quaternion's rotation should be created.

        """
        try:
            shape = matrix.shape
        except AttributeError:
            raise TypeError("Invalid matrix type: Input must be a 3x3 or 4x4 numpy array or matrix")
        
        if shape == (3, 3):
            R = matrix
        elif shape == (4,4):
            R = matrix[:-1][:,:-1] # Upper left 3x3 sub-matrix
        else:
            raise ValueError("Invalid matrix shape: Input must be a 3x3 or 4x4 numpy array or matrix")
        
        # Check matrix properties
        if not np.allclose(np.dot(R, R.conj().transpose()), np.eye(3)):
            raise ValueError("Matrix must be orthogonal, i.e. its transpose should be its inverse")
        if not np.isclose(np.linalg.det(R), 1.0):
            raise ValueError("Matrix must be special orthogonal i.e. its determinant must be +1.0")

        def decomposition_method(matrix):
            """ Method supposedly able to deal with non-orthogonal matrices - NON-FUNCTIONAL!
            Based on this method: http://arc.aiaa.org/doi/abs/10.2514/2.4654
            """
            x, y, z = 0, 1, 2 # indices
            K = np.array([
                [R[x,x]-R[y,y]-R[z,z],  R[y,x]+R[x,y],          R[z,x]+R[x,z],          R[y,z]-R[z,y] ],
                [R[y,x]+R[x,y],         R[y,y]-R[x,x]-R[z,z],   R[z,y]+R[y,z],          R[z,x]-R[x,z] ],
                [R[z,x]+R[x,z],         R[z,y]+R[y,z],          R[z,z]-R[x,x]-R[y,y],   R[x,y]-R[y,x] ],
                [R[y,z]-R[z,y],         R[z,x]-R[x,z],          R[x,y]-R[y,x],          R[x,x]+R[y,y]+R[z,z] ]])
            K = K / 3.0

            e_vals, e_vecs = np.linalg.eig(K)
            print('Eigenvalues:', e_vals)
            print('Eigenvectors:', e_vecs)
            max_index = np.argmax(e_vals)
            principal_component = e_vecs[max_index]
            return principal_component

        def trace_method(matrix):
            """
            This code uses a modification of the algorithm described in: 
            https://d3cw3dd2w32x2b.cloudfront.net/wp-content/uploads/2015/01/matrix-to-quat.pdf
            which is itself based on the method described here:
            http://www.euclideanspace.com/maths/geometry/rotations/conversions/matrixToQuaternion/
            
            Altered to work with the column vector convention instead of row vectors
            """
            m = matrix.conj().transpose() # This method assumes row-vector and postmultiplication of that vector
            if m[2,2] < 0:
                if m[0,0] > m[1,1]:
                    t = 1 + m[0,0] - m[1,1] - m[2,2]
                    q = [m[1,2]-m[2,1], t, m[0,1]+m[1,0], m[2,0]+m[0,2]]
                else:
                    t = 1 - m[0,0] + m[1,1] - m[2,2]
                    q = [m[2,0]-m[0,2], m[0,1]+m[1,0], t, m[1,2]+m[2,1]]
            else:
                if m[0,0] < -m[1,1]:
                    t = 1 - m[0,0] - m[1,1] + m[2,2]
                    q = [m[0,1]-m[1,0], m[2,0]+m[0,2], m[1,2]+m[2,1], t]
                else:
                    t = 1 + m[0,0] + m[1,1] + m[2,2]
                    q = [t, m[1,2]-m[2,1], m[2,0]-m[0,2], m[0,1]-m[1,0]]

            q = np.array(q)
            q *= 0.5 / sqrt(t);
            return q

        return cls(array=trace_method(R))

    # Initialise from axis-angle
    @classmethod
    def _from_axis_angle(cls, axis, angle):
        """
        Precondition: axis is a valid numpy 3-vector, angle is a real valued angle in radians
        """
        mag_sq = np.dot(axis, axis)
        if mag_sq == 0.0:
            raise ZeroDivisionError("Provided rotation axis has no length")
        # Ensure axis is in unit vector form
        if (abs(1.0 - mag_sq) > 1e-12):
            axis = axis / sqrt(mag_sq)
        theta = angle / 2.0
        r = cos(theta)
        i = axis * sin(theta)

        return cls(r, i[0], i[1], i[2])

    @classmethod
    def random(cls):
        """ Generate a random unit quaternion. 

        Uniformly distributed across the rotation space
        As per: http://planning.cs.uiuc.edu/node198.html
        """
        r1 = random.random()
        r2 = random.random()
        r3 = random.random()

        q1 = sqrt(1.0 - r1) * (sin(2 * pi * r2))
        q2 = sqrt(1.0 - r1) * (cos(2 * pi * r2))
        q3 = sqrt(r1)       * (sin(2 * pi * r3))
        q4 = sqrt(r1)       * (cos(2 * pi * r3))

        return cls(q1, q2, q3, q4)

    # Representation
    def __str__(self):
        return "{:.3f} {:+.3f}i {:+.3f}j {:+.3f}k".format(self.q[0], self.q[1], self.q[2], self.q[3])

    def __repr__(self):
        return "Quaternion({}, {}, {}, {})".format(repr(self.q[0]), repr(self.q[1]), repr(self.q[2]), repr(self.q[3]))

    def __format__(self, formatstr):
        if formatstr.strip() == '': # Defualt behaviour mirrors self.__str__()
            formatstr = '+.3f'

        string = \
            "{:" + formatstr +"} "  + \
            "{:" + formatstr +"}i " + \
            "{:" + formatstr +"}j " + \
            "{:" + formatstr +"}k"
        return string.format(self.q[0], self.q[1], self.q[2], self.q[3])

    # Type Conversion
    def __int__(self):
        """ Implements type conversion to int.

        Truncates the Quaternion object by only considering the real 
        component and rounding to the next integer value towards zero.
        Note: to round to the closest integer, use int(round(float(q)))
        """
        return int(self.q[0])

    def __float__(self):
        """ Implements type conversion to float.

        Truncates the Quaternion object by only considering the real 
        component.
        """
        return self.q[0]

    def __complex__(self):
        """ Implements type conversion to complex.

        Truncates the Quaternion object by only considering the real 
        component and the first imaginary component. 
        This is equivalent to a projection from the 4-dimensional hypersphere 
        to the 2-dimensional complex plane.
        """
        return complex(self.q[0], self.q[1])

    def __bool__(self):
        return not (self == Quaternion(0.0))

    def __nonzero__(self):
        return not (self == Quaternion(0.0))

    def __invert__(self):
        return (self == Quaternion(0.0))

    # Comparison
    def __eq__(self, other):
        """
        Returns true if the following is true for each element:
        `absolute(a - b) <= (atol + rtol * absolute(b))`
        """
        if isinstance(other, self.__class__):
            r_tol = 1.0e-13
            a_tol = 1.0e-14
            try:
                isEqual = np.allclose(self.q, other.q, rtol=r_tol, atol=a_tol)
            except AttributeError:
                raise AttributeError("Error in internal quaternion representation means it cannot be compared like a numpy array.")
            return isEqual
        return self.__eq__(self.__class__(other))

    # Negation
    def __neg__(self):
        return self.__class__(array= -self.q)

    # Addition
    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(array=self.q + other.q)
        return self + self.__class__(other)

    def __iadd__(self, other):
        return self + other

    def __radd__(self, other):
        return self + other

    # Subtraction
    def __sub__(self, other):
        return self + (-other)

    def __isub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return -(self - other)

    # Multiplication
    def __mul__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(array=np.dot(self._q_matrix(), other.q))
        return self * self.__class__(other)
    
    def __imul__(self, other):
        return self * other

    def __rmul__(self, other):
        return self.__class__(other) * self

    # Division
    def __div__(self, other):
        if isinstance(other, self.__class__):
            if other == self.__class__(0.0):
                raise ZeroDivisionError("Quaternion divisor must be non-zero")
            return self * other.inverse()
        return self.__div__(self.__class__(other))

    def __idiv__(self, other):
        return self.__div__(other)

    def __rdiv__(self, other):
        return self.__class__(other) * self.inverse()

    def __truediv__(self, other):
        return self.__div__(other)

    def __itruediv__(self, other):
        return self.__idiv__(other)

    def __rtruediv__(self, other):
        return self.__rdiv__(other)

    # Exponentiation
    def __pow__(self, exponent):
        exponent = float(exponent) # Explicitly reject non-real exponents
        theta = acos(self.scalar() / self.norm())
        n = self.vector() / np.linalg.norm(self.vector())
        return (self.norm() ** exponent) * Quaternion(scalar=cos(exponent * theta), vector=(n * sin(exponent * theta)))

    def __ipow__(self, other):
        return self ** other

    def __rpow__(self, other):
        return other ** float(self)

    # Quaternion Features
    def _vector_conjugate(self):
        return np.hstack((self.q[0], -self.q[1:4]))

    def _sum_of_squares(self):
        return np.dot(self.q, self.q)

    def conjugate(self):
        # Return vector conjugate encapsulated in a new instance
        return self.__class__(scalar=self.scalar(), vector= -self.vector())

    def inverse(self):
        return self.__class__(array=(self._vector_conjugate() / self._sum_of_squares()))

    def norm(self): # -> scalar double
        """ Return L2 norm of the quaternion 4-vector 

        Returns the square root of the sum of the squares of the elements of q
        Slow but accurate. If speed is a concern, consider using _fast_normalise() instead
        """
        mag_squared = self._sum_of_squares()
        return sqrt(mag_squared)

    def magnitude(self):
        return self.norm()

    def _normalise(self):
        """
        Object is guaranteed to be a unit quaternion after calling this operation
        """
        if not self.is_unit():
            self.q = self.q / self.norm()

    def _fast_normalise(self):
        """ Normalise the object to a unit quaternion using a fast approximation method if appropriate

        Object is guaranteed to be a quaternion of approximately unit length after calling this operation
        """
        if not self.is_unit():
            mag_squared = np.dot(self.q, self.q)
            if (abs(1.0 - mag_squared) < 2.107342e-08):
                mag =  ((1.0 + mag_squared) / 2.0) # More efficient. Pade approximation valid if error is small 
            else:
                mag =  sqrt(mag_squared) # Error is too big, take the performance hit to calculate the square root properly

            self.q = self.q / mag

    def normalised(self):
        """ Return a unit quaternion object (versor) representing the same rotation as this

        Result is guaranteed to be a unit quaternion
        """
        q = Quaternion(self)
        q._normalise()
        return q

    def unit(self):
        """ Return a unit quaternion object (versor) representing the same rotation as this

        Result is guaranteed to be a unit quaternion
        """
        return self.normalised()

    def is_unit(self, tolerance=1e-14):
        """ Determine whether the quaternion is of unit length to within a specified tolerance value
        """
        return abs(1.0 - self._sum_of_squares()) < tolerance # if _sum_of_squares is 1, norm is 1. This saves a call to sqrt()

    def _q_matrix(self):
        return np.array([
            [self.q[0], -self.q[1], -self.q[2], -self.q[3]],
            [self.q[1],  self.q[0], -self.q[3],  self.q[2]],
            [self.q[2],  self.q[3],  self.q[0], -self.q[1]],
            [self.q[3], -self.q[2],  self.q[1],  self.q[0]]])

    def _q_bar_matrix(self):
        return np.array([
            [self.q[0], -self.q[1], -self.q[2], -self.q[3]],
            [self.q[1],  self.q[0],  self.q[3], -self.q[2]],
            [self.q[2], -self.q[3],  self.q[0],  self.q[1]],
            [self.q[3],  self.q[2], -self.q[1],  self.q[0]]])

    def _rotate_quaternion(self, q):
        """ Rotate a quaternion vector using the stored rotation.

        The input q is the vector to be rotated, in quaternion form (0 + xi + yj + kz)
        """
        self._normalise()
        return self * q * self.conjugate()

    def rotate(self, vector):
        """ Rotate a vector using the quaternion's stored rotation (similarity transform)

        Input vector can be specified as another (pure imaginary) quaternion 
        or a 3-vector described by a tuple, list or numpy array of length 3.

        Output is returned in the type of the provided input vector
        """
        if isinstance(vector, self.__class__):
            return self._rotate_quaternion(vector)
        q = Quaternion(vector=vector)
        a = self._rotate_quaternion(q).vector()
        if isinstance(vector, list):
            l = [x for x in a]
            return l
        elif isinstance(vector, tuple):
            l = [x for x in a]
            return tuple(l)
        else:
            return a

    @classmethod
    def slerp(cls, q0, q1, amount=0.5):
        # Ensure quaternion inputs are unit quaternions and 0 <= amount <=1
        q0._fast_normalise()
        q1._fast_normalise()
        amount = np.clip(amount, 0, 1)

        return ((q1 * q0.inverse()) ** amount) * q0
        
    @classmethod
    def intermediates(cls, q0, q1, n, include_endpoints=False):
        step_size = 1.0 / (n + 1)
        if include_endpoints:
            steps = [i * step_size for i in range(0, n + 2)]
        else:
            steps = [i * step_size for i in range(1, n + 1)]
        for step in steps:
            yield cls.slerp(q0, q1, step)

    def rotation_matrix(self):
        self._normalise()
        product_matrix = np.dot(self._q_matrix(), self._q_bar_matrix().conj().transpose())
        return product_matrix[1:][:,1:]

    def transformation_matrix(self):
        t = np.array([[0.0], [0.0], [0.0]])
        Rt = np.hstack([self.rotation_matrix(), t])
        return np.vstack([Rt, np.array([0.0, 0.0, 0.0, 1.0])])

    def _wrap_angle(self, theta):
            """ Wrap any angle to lie between -pi and pi 

            Odd multiples of pi are wrapped to +pi (as opposed to -pi)
            """
            result = ((theta + pi) % (2*pi)) - pi
            if result == -pi: result = pi
            return result

    def axis(self, undefined=np.zeros(3)):
        tolerance = 1e-17
        self._normalise()
        #partial_angle = acos(self.q[0])
        #axis = np.array([self.q[1] / sin(partial_angle), self.q[2] / sin(partial_angle), self.q[3] / sin(partial_angle)])
        norm = np.linalg.norm(self.vector())
        if norm < tolerance:
            # Here there are an infinite set of possible axes, use what has been specified as an undefined axis.
            return undefined 
        else:
            return self.vector() / norm

    def angle(self):
        self._normalise()
        norm = np.linalg.norm(self.vector())
        return self._wrap_angle(2.0 * atan2(norm,self.scalar()))

    def scalar(self):
        """ Return the real or scalar component of the quaternion object

        Result is a real number i.e. float
        """
        return self.q[0]

    def vector(self):
        """ Return the imaginary or vector component of the quaternion object

        Result is a numpy 3-array of floats
        Result is not guaranteed to be a unit vector
        """
        return self.q[1:4]

    def real(self):
        """ Return the real or scalar component of the quaternion object

        Result is a real number i.e. float
        """
        return self.scalar()

    def imaginary(self):
        """ Return the imaginary or vector component of the quaternion object

        Result is a numpy 3-array of floats
        Result is not guaranteed to be a unit vector
        """
        return self.vector()

    def elements(self):
        """ Return all the elements of the quaternion object

        Result is a numpy 4-array of floats
        Result is not guaranteed to be a unit vector
        """
        return self.q

    def __getitem__(self, index):
        index = int(index)
        return self.q[index]

    def __setitem__(self, index, value):
        index = int(index)
        self.q[index] = float(value)


    def __deepcopy__(self):
        return self.__class__(self)
