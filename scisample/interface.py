"""
Interface definition for ``Sampler`` objects.

This will be moved to ``codepyinterfaces`` the next time that package
is updated.
"""
###############################################################################
# Copyright (c) 2021, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory
# Written by Christopher Krenn, krenn1@llnl.gov.
#
# LLNL-CODE-815909
# All rights reserved.
# This file is part of scisample, Version: 0.0.1.
#
# For details, see https://github.com/LLNL/scisample.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###############################################################################
###############################################################################
# Copyright (c) 2021, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory
# Written by Christopher Krenn, krenn1@llnl.gov.
#
# LLNL-CODE-815909
# All rights reserved.
# This file is part of scisample, Version: 0.0.1.
#
# For details, see https://github.com/LLNL/scisample.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###############################################################################

import abc


class SamplerInterface(abc.ABC):
    """
    Abstract interface for sampler objects.
    """

    @property
    @abc.abstractmethod
    def data(self):
        """
        Sampler data from the configuration file.
        """
        pass

    @abc.abstractmethod
    def check_validity(self):
        """
        Check validity of the sampler. This will raise a
        `SamplingError` if the sampler is not valid, but return
        otherwise.
        """
        pass

    @abc.abstractmethod
    def get_samples(self):
        """
        Get samples from the sampler.

        This should return samples as a list of dictionaries, with the
        sample variables as the keys:

        .. code:: python

            [{'b': 0.89856, 'a': 1}, {'b': 0.923223, 'a': 1}, ... ]
        """
        pass

    @property
    @abc.abstractmethod
    def parameters(self):
        """
        Return a of list of the parameters being generated by the
        sampler.
        """
        pass

    @property
    @abc.abstractmethod
    def parameter_block(self):
        """
        Converts samples to parameter dictionary for ``codepy setup`` and ``codepy run``
        """ # noqa
        pass
