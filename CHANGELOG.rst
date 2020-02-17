^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Changelog for package pyquaternion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

0.9.5 (2020-02-17)
------------------
Post ROS package conversion:
* Change exec depend naming from numpy to python-numpy
* Add numpy dependency to package.xml
* Create catkin package, rename and move some files
* Fix casting error in trace_method
* Add setter for vector
Pre ROS package conversion:
* Merge pull request `#49 <https://github.com/Achllle/pyquaternion/issues/49>`_ from KieranWynn/handedness-clarification
  reference frame clarification
* Replac kwargs with atol and rtol explicitly
* Updated index.md with examples of how to use new options
* Update deploy config
* Merge pull request `#46 <https://github.com/Achllle/pyquaternion/issues/46>`_ from e-kwsm/special-methods
  Add special methods: __abs_\_; __matmul_\_, __imatmul_\_ and __rmatmul\_\_
* minor fixes
* Quaternion from Matrix Optional Args
* Merge pull request `#43 <https://github.com/Achllle/pyquaternion/issues/43>`_ from Hojjatrt/master
* Contributors: Achille, Daniel Olshansky, Eisuke Kawashima, Hojjatrt, Kieran Wynn
