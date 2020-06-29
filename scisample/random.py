"""
Module defining the random sampler object.
"""

import logging
import random

from contextlib import suppress
from scisample.base_sampler import BaseSampler
from scisample.utils import log_and_raise_exception


LOG = logging.getLogger(__name__)


class RandomSampler(BaseSampler):
    """
    Class defining basic random sampling.

    This is similar to the ``csv`` functionality of ``codepy setup``
    and ``codepy run``.  Its sampler data takes two blocks:
    ``constants`` and ``parameters``:

    .. code:: yaml

        sampler:
            type: random
            num_samples: 30
            previous_samples: samples.csv # optional
            constants:
                X1: 20
            parameters:
                X2:
                    min: 5
                    max: 10
                X3:
                    min: 5
                    max: 10

    A total of ``num_samples`` will be generated. Entries in the ``constants``
    dictionary will be added to all samples. Entries in the ``parameters``
    block will be selected from a range of ``min`` to ``max``.  The result of
    the above block would something like:

    .. code:: python

        [{X1: 20, X2: 5.632222227306036, X3: 6.633392173916806},
         {X1: 20, X2: 7.44369755967992, X3: 8.941266067294213}]
    """

    def is_valid(self):
        """
        Check if the sampler is valid.

        Checks the sampler data against the built-in schema.

        Checks that all entries in ``parameters`` have the same
        length.

        :returns: True if the schema is valid, False otherwise.
        """
        LOG.info("entering RandomSampler.is_valid()")
        if not super(RandomSampler, self).is_valid():
            return False

        self._check_variables()

        # @TODO: test that file exists and it contains the right parameters
        if 'previous_samples' in self.data.keys():
            pass

        # @TODO: add error check to schema
        for key, value in self.data["parameters"].items():
            if not str(value["min"]).isnumeric():
                log_and_raise_exception(
                    "parameter must have a numeric minimum")
            if not str(value["max"]).isnumeric():
                log_and_raise_exception(
                    "parameter must have a numeric maximum")

        return True

    @property
    def parameters(self):
        """
        Return a of list of the parameters being generated by the
        sampler.
        """
        LOG.info("entering RandomSampler.parameters")
        LOG.info("self.data: \n" + str(self.data))
        parameters = []
        with suppress(KeyError):
            parameters.extend(list(self.data['constants'].keys()))
        with suppress(KeyError):
            parameters.extend(list(self.data['parameters'].keys()))
        LOG.info("parameters: \n" + str(parameters))

        return parameters

    def get_samples(self):
        """
        Return set of random samples based on specification in sampling_dict.

        Prototype dictionary:

        num_samples: 5
        previous_samples: samples.csv # optional
        constants:
            X1: 20
        parameters:
            x2:
                min: 5
                max: 1
            x3:
                min: 5
                max: 10
        """
        LOG.info("Entering ColumnListSampler.get_samples()")
        if self._samples is not None:
            return self._samples

        self._samples = []

        random_list = []
        min_dict = {}
        range_dict = {}
        for key, value in self.data["parameters"].items():
            min_dict[key] = value["min"]
            range_dict[key] = value["max"] - value["min"]
        for i in range(self.data["num_samples"]):
            random_dictionary = {}
            for key, value in self.data["parameters"].items():
                random_dictionary[key] = (
                    min_dict[key] + random.random() * range_dict[key])
            random_list.append(random_dictionary)
        LOG.info("random.get_samples samples: \n" + str(random_list))

        for i in range(len(random_list)):
            new_sample = {}

            with suppress(KeyError):
                new_sample.update(self.data['constants'])

            with suppress(KeyError):
                for key, value in random_list[i].items():
                    new_sample[key] = value

            self._samples.append(new_sample)

        return self._samples
