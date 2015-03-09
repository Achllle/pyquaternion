# Quaternion Features
This page defines features available for pyquaternion's Quaternion objects

The code examples below assume the existence of a Quaternion object. You can recreate this by running the following in your Python interpreter of choice:
	
	my_quaternion = Quaternion.random()

## Norm
> **`norm()` or `magnitude()`**

L2 norm of the quaternion 4-vector 

This should be 1.0 for a unit quaternion (versor)

**Returns:** a scalar real number representing the square root of the sum of the squares of the elements of the quaternion.

	my_quaternion.norm()
	my_quaternion.magnitude()
	
----

> **`is_unit(tolerance=1e-14)`**

**Params:** 
	
* `tolerance` - [optional] - maximum absolute value by which the norm can differ from 1.0 for the object to be considered a unit quaternion. Defaults to `1e-14`.

**Returns:** `True` if the Quaternion object is of unit length to within the specified tolerance value. `False` otherwise.


	
## Inversion
> **`inverse()`**

Inverse of the quaternion object

For a unit quaternion, this is the inverse rotation, i.e. when combined with the original rotation, will result in the null rotation.

**Returns:** a new Quaternion object representing the inverse of this object
	
	inv_quaternion = my_quaternion.inverse()
	
## Conjugation
> **`conjugate()`**

Quaternion conjugate

For a unit quaternion, this is the same as the inverse.

**Returns:** a new Quaternion object clone with its vector part negated

	conj_quaternion = my_quaternion.conjugate()
	
## Normalisation
> **`normalised()` or `unit()`**

Get a unit quaternion (versor) copy of this Quaternion object.

A unit quaternion has a `norm()` of 1.0

**Returns:** a new Quaternion object clone that is guaranteed to be a unit quaternion
	
	unit_quaternion = my_quaternion.normalise()
	unit_quaternion = my_quaternion.unit()
	

## Rotation
> **`rotate(vector)`**

Rotate a 3D vector by the rotation stored in the Quaternion object

**Params:**
	
* `vector` - a 3-vector specified as any ordered sequence of 3 real numbers corresponding to x, y, and z values. Some types that are recognised are: numpy arrays, lists and tuples. A 3-vector can also be represented by a Quaternion object who's scalar part is 0 and vector part is the required 3-vector. Thus it is possible to call `Quaternion.rotate(q)` with another quaternion object as an input.

**Returns:** the rotated vector returned as the same type it was specified at input.

	rotated_tuple 		= my_quaternion.rotate((1, 0, 0)) # Returns a tuple
	rotated_list  		= my_quaternion.rotate([1.0, 0.0, 0.0]) # Returns a list
	rotated_array 		= my_quaternion.rotate(numpy.array([1.0, 0.0, 0.0])) # Returns a Numpy 3-array
	rotated_quaternion	= my_quaternion.rotate(Quaternion(vector=[1, 0, 0])) # Returns a Quaternion object

**Raises:**

* `TypeError` if any of the vector elements cannot be converted to a real number.

* `ValueError` if `vector` cannot be interpreted as a 3-vector or a Quaternion object.


## Interpolation

> **`Quaternion.slerp(q0, q1, amount=0.5)`** - *class method*

Find a valid quaternion rotation at a specified distance along the minor arc of a great circle passing through any two existing quaternion endpoints lying on the unit radius hypersphere. [Source](http://en.wikipedia.org/wiki/Slerp#Quaternion_Slerp)

This is a class method and is called as a method of the class itself rather than on a particular instance.

**Params:**

* `q0` - first endpoint rotation as a Quaternion object
* `q1` - second endpoint rotation as a Quaternion object
* `amount` - interpolation parameter between 0 and 1. This describes the linear placement position of the result along the arc between endpoints; 0 being at `q0` and 1 being at `q1`. Defaults to the midpoint (0.5).

**Returns:**
a new Quaternion object representing the interpolated rotation. This is guaranteed to be a unit quaternion.

> **Note:** This feature only makes sense when interpolating between unit quaternions (those lying on the unit radius hypersphere). Calling this method will implicitly normalise the endpoints to unit quaternions if they are not already unit length.

	q0 = Quaternion(axis=[1, 1, 1], angle=0.0)
	q1 = Quaternion(axis=[1, 1, 1], angle=3.141592)
	q  = Quaternion.slerp(q0, q1, 2.0/3.0) # Rotate 120 degrees (2 * pi / 3)

-----

> **`Quaternion.intermediates(q_start, q_end, n, include_endpoints=False)`** - *class method*

Generator method to get an iterable sequence of `n` evenly spaced quaternion rotations between any two existing quaternion endpoints lying on the unit radius hypersphere. This is a convenience function that is based on `Quaternion.slerp()` as defined above.

This is a class method and is called as a method of the class itself rather than on a particular instance.

**Params:**

* `q_start` - initial endpoint rotation as a Quaternion object
* `q_end` - final endpoint rotation as a Quaternion object
* `n` - number of intermediate quaternion objects to include within the interval
* `include_endpoints` - [optional] - If set to `True`, the sequence of intermediates will be 'bookended' by `q_start` and `q_end`, resulting in a sequence length of `n + 2`. If set to `False`, endpoints are not included. Defaults to `False`.

**Returns:** 
a generator object iterating over a sequence of intermediate quaternion objects.

**Note:** This feature only makes sense when interpolating between unit quaternions (those lying on the unit radius hypersphere). Calling this method will implicitly normalise the endpoints to unit quaternions if they are not already unit length.
	
	q0 = Quaternion(axis=[1, 1, 1], angle=0.0)
	q1 = Quaternion(axis=[1, 1, 1], angle=2 * 3.141592 / 3)
	for q in Quaternion.intermediates(q0, q1, 8, include_endpoints=True):
		v = q.rotate([1, 0, 0])
		print(v)

## Conversion to matrix form
> **`rotation_matrix()` & `transformation_matrix()`**

Get the 3x3 rotation or 4x4 homogeneous transformation matrix equivalent of the quaternion rotation.

**Returns:**

* `Quaternion.rotation_matrix()` : a 3x3 orthogonal rotation matrix as a 3x3 Numpy array
* `Quaternion.transformation_matrix()` : a 4x4 homogeneous transformation matrix as a 4x4 Numpy array

**Note 1:** This feature only makes sense when referring to a unit quaternion. Calling this method will implicitly normalise the Quaternion object to a unit quaternion if it is not already one.

**Note 2:** Both matrices and quaternions avoid the singularities and discontinuities involved with rotation in 3 dimensions by adding extra dimensions. This has the effect that different values could represent the same rotation, for example quaternion q and -q represent the same rotation. It is therefore possible that, when converting a rotation sequence, the output may jump between different but equivalent forms. This could cause problems where subsequent operations such as differentiation are done on this data. Programmers should be aware of this issue.
	
	R = my_quaternion.rotation_matrix() 		# 3x3 rotation matrix
	T = my_quaternion.transformation_matrix()   # 4x4 transformation matrix

## Accessing rotation axis
> **`axis()`**

Get the axis or vector about which the quaternion rotation occurs

For a null rotation (a purely real quaternion), the rotation angle will always be `0`, but the rotation axis is undefined. It is by default assumed to be `[0, 0, 0]`.

**Params: **

* `undefined` - [optional] - specify the axis vector that should define a null rotation. This is geometrically meaningless, and could be any of an infinite set of vectors, but can be specified if the default (`[0, 0, 0]`) causes undesired behaviour.

**Returns:** a Numpy unit 3-vector describing the Quaternion object's axis of rotation.

**Note 1:** This feature only makes sense when referring to a unit quaternion. Calling this method will implicitly normalise the Quaternion object to a unit quaternion if it is not already one.

**Note 2:** Both matrices and quaternions avoid the singularities and discontinuities involved with rotation in 3 dimensions by adding extra dimensions. This has the effect that different values could represent the same rotation, for example quaternion q and -q represent the same rotation. It is therefore possible that, when converting a rotation sequence to axis/angle representation, the output may jump between different but equivalent forms. This could cause problems where subsequent operations such as differentiation are done on this data. Programmers should be aware of this issue.


	u = my_quaternion.axis() # Unit vector about which rotation occurs


## Accessing rotation angle 
> **`angle()`**

Get the angle (in radians) describing the magnitude of the quaternion rotation about its rotation axis. This is guaranteed to be within the range (-pi:pi) with the direction of rotation indicated by the sign.

When a particular rotation describes a 180 degree rotation about an arbitrary axis vector `v`, the conversion to axis / angle representation may jump discontinuously between all permutations of `(-pi, pi)` and `(-v, v)`, each being geometrically equivalent (see Note 2 below).

**Returns:** a real number in the range (-pi:pi) describing the angle of rotation in radians about a Quaternion object's axis of rotation. 

**Note 1:** This feature only makes sense when referring to a unit quaternion. Calling this method will implicitly normalise the Quaternion object to a unit quaternion if it is not already one.

**Note 2:** Both matrices and quaternions avoid the singularities and discontinuities involved with rotation in 3 dimensions by adding extra dimensions. This has the effect that different values could represent the same rotation, for example quaternion q and -q represent the same rotation. It is therefore possible that, when converting a rotation sequence to axis/angle representation, the output may jump between different but equivalent forms. This could cause problems where subsequent operations such as differentiation are done on this data. Programmers should be aware of this issue.


	theta = my_quaternion.angle() # Magnitude of rotation about the prescribed axis


## Accessing real components
> **`scalar()` or `real()`**

Get the real or scalar component of the Quaternion object

A quaternion can be described in terms of a scalar and vector part, q = [r, **v**] where:

* r is the scalar coefficient of the real part of the quaternion i.e. **a** in a + b*i* + c*j* + d*k*

* **v** is the 3-vector of coefficients to the imaginary parts of the quaternion i.e. [b, c, d] in a + b*i* + c*j* + d*k*

This method returns r

**Returns** the scalar, real valued element of the Quaternion object

	r = my_quaternion.scalar()
	r = my_quaternion.real()

## Accessing imaginary components
> **`vector()` or `imaginary()`**

Get the imaginary or vector component of the Quaternion object. This can be used, for example, to extract the stored vector when a pure-imaginary quaternion object is used to describe a vector within the three-dimensional vector space.

A quaternion can be described in terms of a scalar and vector part, q = [r, **v**] where:

* r is the scalar coefficient of the real part of the quaternion i.e. **a** in a + b*i* + c*j* + d*k*

* **v** is the 3-vector of coefficients to the imaginary parts of the quaternion i.e. [b, c, d] in a + b*i* + c*j* + d*k*

This method returns **v**

**Returns** Numpy 3-array of the 3 imaginary elements of the Quaternion object

	v = my_quaternion.vector()
	v = my_quaternion.imaginary()

## Accessing individual elements
> **`elements()`**

Return all four elements of the quaternion object. Result is not guaranteed to be a unit 4-vector.

**Returns:** a numpy 4-array of real numbered coefficients.

	a = my_quaternion.elements()
	print("{} + {}i + {}j + {}k".format(a[0], a[1], a[2], a[3]))

---
 
> **`__getitem__(index)`**

**Returns:** the real numbered element at the specified index in the quaternion 4-array

**Params:**

* `index` - integer in the range [-4:3] inclusive

```
print("{} + {}i + {}j + {}k".format(my_quaternion[0], my_quaternion[1], my_quaternion[2], my_quaternion[3]))
print("{} + {}i + {}j + {}k".format(my_quaternion[-4], my_quaternion[-3], my_quaternion[-2], my_quaternion[-1]))
```

**Raises:** 

* `IndexError` if the index provided is invalid

* `TypeError` or `ValueError` if the index cannot be interpreted as an integer

## Modifying individual elements
> **`__setitem__(index, value)`**

Set the element at the specified index in the quaternion 4-array to the specified value.

**Params:**

* `index` - integer in the range [-4:3] inclusive
* `value` - real value to be inserted into the quaternion array at `index`

```
>>> str(my_quaternion)
'-0.653 -0.127i -0.220j +0.714k'
>>> my_quaternion[2] = 9
>>> str(my_quaternion)
'-0.653 -0.127i +9.000j +0.714k'
>>>
```

**Raises:**

* `IndexError` if the index provided is invalid

* `TypeError` or `ValueError` if the value cannot be interpreted as a real number

	



