"""
Module defining the BaseSampler class.
"""

import logging
from contextlib import suppress

from jsonschema import ValidationError

from scisample.interface import SamplerInterface
from scisample.schema import validate_sampler
from scisample.utils import (_convert_dict_to_maestro_params, find_duplicates,
                             log_and_raise_exception)

# @TODO: can this duplicate code be removed?
MAESTROWF = False
with suppress(ModuleNotFoundError):
    from maestrowf.datastructures.core import ParameterGenerator
    MAESTROWF = True

PANDAS_PLUS = False
with suppress(ModuleNotFoundError):
    import pandas as pd
    import numpy as np
    import scipy.spatial as spatial
    PANDAS_PLUS = True

LOG = logging.getLogger(__name__)


class BaseSampler(SamplerInterface):
    """
    Base sampler class.
    """
    # @TODO: define SAMPLE_FUNCTIONS_DICT automatically:
    # https://stackoverflow.com/questions/3862310/how-to-find-all-the-subclasses-of-a-class-given-its-namedefine keywords # noqa
    #
    # def all_subclasses(cls):
    #     return set(cls.__subclasses__()).union(
    #         [s for c in cls.__subclasses__() for s in all_subclasses(c)])


    _ALLOWED_SAMPLING_DICT = {
        'best_candidate': 'BestCandidateSampler',
        'column_list': 'ColumnListSampler',
        'cross_product': 'CrossProductSampler',
        'csv': 'CsvSampler',
        'custom': 'CustomSampler',
        'list': 'ListSampler',
        'random': 'RandomSampler',
    }
    
    ALLOWED_SAMPLING_KEYS = list(_ALLOWED_SAMPLING_DICT.keys())
    """
    Examples of yaml sampling specifications:

    .. code:: yaml

        sampler:
            type: best_candidate
            num_samples: 30
            previous_samples: samples.csv # not supported yet
            constants:
                X1: 20
            parameters:
                X2:
                    min: 5
                    max: 10
                X3:
                    min: 5
                    max: 10

        sampler:
            type: column_list
            constants:
                X1: 20
            parameters: |
                X2       X3
                5        5
                10       10

         sampler:
            type: cross_product
            constants:
                X1: 20
            parameters:
                X2: [5, 10]
                X3: [5, 10]  

        sampler:
            type: csv
            csv_file: file_name.csv
            row_headers: True

        sampler:
            type: custom
            function: <name of function>
            module: <path to module containing function>
            args: {} # Dictionary of keyword arguments to pass
                     # To the function.

        sampler:
            type: list
            constants:
                X1: 20
            parameters:
                X2: [5, 10]
                X3: [5, 10]  

        sampler:
            type: random
            num_samples: 5
            previous_samples: samples.csv # not supported yet
            constants:
                X1: 20
            parameters:
                X2:
                    min: 5
                    max: 10
                X3:
                    min: 5
                    max: 10                                   
        """


    def __init__(self, data):
        """
        Initialize the sampler.

        :param data: Dictionary of sampler data.
        """
        self._data = data
        self._samples = None
        self._parameter_block = None
        self._pgen = None

    def check_validity(self):
        # validate data
        try:
            validate_sampler(self.data)
        except ValueError:
            log_and_raise_exception(
                f"No 'type' entry found in sampler data {self.data}")
        except KeyError:
            log_and_raise_exception(
                f"Sampler type {self.data['type']} not found in schema")
        except ValidationError:
            log_and_raise_exception("Sampler data is invalid")

    @property
    def data(self):
        """
        Sampler data block.
        """
        return self._data

    def _parameters_constants_parameters_only(self):
        """
        Return a of list of the parameters being generated by the
        sampler when only constants and parameters are used.
        """
        parameters = []
        with suppress(KeyError):
            parameters.extend(list(self.data['constants'].keys()))
        with suppress(KeyError):
            parameters.extend(list(self.data['parameters'].keys()))
            
        return parameters

    def _check_variables(self):
        self._check_variables_strings()
        self._check_variables_existence()
        self._check_variables_for_dups()

    def _check_variables_strings(self):
        for parameter in self.parameters:
            if not isinstance(parameter, str):
                log_and_raise_exception(
                    "constants and parameters must be strings")

    def _check_variables_existence(self):
        if len(self.parameters) == 0:
            log_and_raise_exception(
                "Either constants or parameters must be included in the " +
                "sampler data")

    def _check_variables_for_dups(self):
        if len(self.parameters) != len(set(self.parameters)):
            dupes = set(find_duplicates(self.parameters))
            log_and_raise_exception(
                "The following constants or parameters are defined more " +
                "than once: " + str(dupes))

    @property
    def parameter_block(self):
        """
        Converts samples to parameter dictionary for ``codepy setup`` and ``codepy run``

        The keys are the labels and the values are a string version of the
        list, so it can be easily passed to Jinja.
        """ # noqa
        if self._parameter_block is None:
            self._parameter_block = {}
            for sample in self.get_samples():
                for key, value in sample.items():
                    if key not in self._parameter_block:
                        self._parameter_block[key] = {
                            "values": [],
                            "label": f"{key}.%%",
                        }
                    self._parameter_block[key]["values"].append(value)

        return self._parameter_block

    @property
    def maestro_pgen(self):
        """
        Returns a maestrowf Parameter Generator object containing samples
        """
        if not MAESTROWF:
            raise Exception("maestrowf is not installed\n" +
                            "the maestro_pgen is not supported")
        if self._pgen is not None:
            return self._pgen

        pgen = ParameterGenerator()
        params = _convert_dict_to_maestro_params(self.get_samples())

        for key, value in params.items():
            pgen.add_parameter(key, value["values"], value["label"])

        self._pgen = pgen
        return pgen

    def downselect(self, samples):
        """
        Downselect samples based on specification in sampling_dict.

        Prototype dictionary::

           num_samples: 30
           previous_samples: samples.csv # optional
           parameters:
               X1:
                   min: 10
                   max: 50
               X2:
                   min: 10
                   max: 50
        """
        if not PANDAS_PLUS:
            log_and_raise_exception(
                "This function requires pandas, numpy & scipy packages")

        df = pd.DataFrame.from_dict(self._samples)
        columns = self.parameters
        ndims = len(columns)
        candidates = df[columns].values.tolist()
        num_points = samples

        if not('previous_samples' in self.data.keys()):
            sample_points = []
            sample_points.append(candidates[0])
            new_sample_points = []
            new_sample_points.append(candidates[0])
            new_sample_ids = []
            new_sample_ids.append(0)
            n0 = 1
        else:
            try:
                previous_samples = pd.read_csv(self.data["previous_samples"])
            except ValueError:
                raise Exception("Error opening previous_samples datafile:" +
                                self.data["previous_samples"])
            sample_points = previous_samples[columns].values.tolist()
            new_sample_points = []
            new_sample_ids = []
            n0 = 0

        mins = np.zeros(ndims)
        maxs = np.zeros(ndims)

        first = True
        for i, candidate in enumerate(candidates):
            for j in range(ndims):
                if first:
                    mins[j] = candidate[j]
                    maxs[j] = candidate[j]
                    first = False
                else:
                    mins[j] = min(candidate[j], mins[j])
                    maxs[j] = max(candidate[j], maxs[j])
        print("extrema for new input_labels: ", mins, maxs)
        print("down sampling to %d best candidates from %d total points." % (
            num_points, len(candidates)))
        bign = len(candidates)

        for n in range(n0, num_points):
            px = np.asarray(sample_points)
            tree = spatial.KDTree(px)
            j = bign
            d = 0.0
            for i in range(1, bign):
                pos = candidates[i]
                dist = tree.query(pos)[0]
                if dist > d:
                    j = i
                    d = dist
            if j == bign:
                raise Exception(
                    "During 'downselect', failed to find any "
                    "candidates in the tree.")
            else:
                new_sample_points.append(candidates[j])
                sample_points.append(candidates[j])
                new_sample_ids.append(j)

        new_samples_df = pd.DataFrame(columns=df.keys().tolist())
        for new_sample_id in new_sample_ids:
            new_samples_df = new_samples_df.append(df.iloc[new_sample_id])

        self._samples = new_samples_df.to_dict(orient='records')
