# Released under the MIT License. See LICENSE for details.
#
# pylint: disable=missing-docstring, invalid-name
from __future__ import annotations

# This file is exec'ed by the spinoff system, allowing us to define
# values and behavior for this feature-set here in a way that can be
# type-checked alongside other project Python code.

from batools.featureset import FeatureSet

# Grab the FeatureSet we should apply to.
fset = FeatureSet.get_active()

fset.requirements = set()

fset.has_native_python_module = False

# Bits of code we're using that don't conform to our feature-set based
# namespace scheme.
fset.cpp_namespace_check_disable_files = {
    'src/ballistica/core/platform/android/utf8/checked.h',
    'src/ballistica/core/platform/android/utf8/unchecked.h',
    'src/ballistica/core/platform/android/utf8/core.h',
}
