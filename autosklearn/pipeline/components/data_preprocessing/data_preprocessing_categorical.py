from typing import Any, List, Dict, Optional, Tuple, Union

from ConfigSpace.configuration_space import Configuration, ConfigurationSpace

import numpy as np

from sklearn.base import BaseEstimator

from autosklearn.pipeline.components.data_preprocessing.category_shift.\
    category_shift import CategoryShift
from autosklearn.pipeline.components.data_preprocessing.imputation.\
    categorical_imputation import CategoricalImputation
from autosklearn.pipeline.components.data_preprocessing.minority_coalescense \
    import CoalescenseChoice
from autosklearn.pipeline.components.data_preprocessing.categorical_encoding \
    import OHEChoice
from autosklearn.pipeline.components.data_preprocessing.categorical_encoding.encoding import (
    OrdinalEncoding
)
from autosklearn.pipeline.base import (
    BasePipeline,
    DATASET_PROPERTIES_TYPE,
)
from autosklearn.pipeline.constants import DENSE, SPARSE, UNSIGNED_DATA, INPUT


class CategoricalPreprocessingPipeline(BasePipeline):
    """This class implements a pipeline for data preprocessing of categorical features.
    It assumes that the data to be transformed is made only of categorical features.
    The steps of this pipeline are:
        1 - Category shift: Adds 3 to every category value
        2 - Imputation: Assign category 2 to missing values (NaN).
        3 - Minority coalescence: Assign category 1 to all categories whose occurrence
            don't sum-up to a certain minimum fraction
        4 - One hot encoding: usual sklearn one hot encoding

    Parameters
    ----------
    config : ConfigSpace.configuration_space.Configuration
        The configuration to evaluate.

    random_state : int, RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance
        used by `np.random`."""

    def __init__(self,
                 config: Optional[Configuration] = None,
                 steps: Optional[List[Tuple[str, BaseEstimator]]] = None,
                 dataset_properties: Optional[DATASET_PROPERTIES_TYPE] = None,
                 include: Optional[Dict[str, str]] = None,
                 exclude: Optional[Dict[str, str]] = None,
                 random_state: Optional[np.random.RandomState] = None,
                 init_params: Optional[Dict[str, Any]] = None):
        self._output_dtype = np.int32
        super().__init__(
            config, steps, dataset_properties, include, exclude,
            random_state, init_params)

    @staticmethod
    def get_properties(dataset_properties: Optional[DATASET_PROPERTIES_TYPE] = None
                       ) -> Dict[str, Optional[Union[str, int, bool, Tuple]]]:
        return {'shortname': 'cat_datapreproc',
                'name': 'categorical data preprocessing',
                'handles_missing_values': True,
                'handles_nominal_values': True,
                'handles_numerical_features': True,
                'prefers_data_scaled': False,
                'prefers_data_normalized': False,
                'handles_regression': True,
                'handles_classification': True,
                'handles_multiclass': True,
                'handles_multilabel': True,
                'is_deterministic': True,
                # TODO find out if this is right!
                'handles_sparse': True,
                'handles_dense': True,
                'input': (DENSE, SPARSE, UNSIGNED_DATA),
                'output': (INPUT,),
                'preferred_dtype': None}

    def _get_hyperparameter_search_space(
        self,
        include: Optional[Dict[str, str]] = None,
        exclude: Optional[Dict[str, str]] = None,
        dataset_properties: Optional[DATASET_PROPERTIES_TYPE] = None,
    ) -> ConfigurationSpace:
        """Create the hyperparameter configuration space.

        Returns
        -------
        cs : ConfigSpace.configuration_space.Configuration
            The configuration space describing the SimpleRegressionClassifier.
        """
        cs = ConfigurationSpace()

        if dataset_properties is None or not isinstance(dataset_properties, dict):
            dataset_properties = dict()

        cs = self._get_base_search_space(
            cs=cs, dataset_properties=dataset_properties,
            exclude=exclude, include=include, pipeline=self.steps)

        return cs

    def _get_pipeline_steps(self,
                            dataset_properties: Optional[Dict[str, str]] = None,
                            ) -> List[Tuple[str, BaseEstimator]]:
        steps = []

        default_dataset_properties = {}
        if dataset_properties is not None and isinstance(dataset_properties, dict):
            default_dataset_properties.update(dataset_properties)

        steps.extend([
            ("imputation", CategoricalImputation()),
            ("encoding", OrdinalEncoding()),
            ("category_shift", CategoryShift()),
            ("category_coalescence", CoalescenseChoice(default_dataset_properties)),
            ("categorical_encoding", OHEChoice(default_dataset_properties)),
            ])

        return steps

    def _get_estimator_hyperparameter_name(self) -> str:
        return "categorical data preprocessing"
