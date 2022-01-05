"""
controlvariation.py - This module defines a cost function
that penalizes variations of the control parameters.
"""

import jax.numpy as jnp
class ControlVariation():
    """
    This cost penalizes the variations of the control parameters
    from one `control_eval_step` to the next.

    Fields:
    control_size
    cost_multiplier
    cost_normalization_constant
    max_control_norms
    name
    order
    requires_step_evaluation
    """
    name = "control_variation"
    requires_step_evaluation = False

    def __init__(self, control_num,
                 total_time_steps,
                 cost_multiplier=1.,
                 max_control_norms=None,
                 order=1):
        """
        See class fields for arguments not listed here.

        Arguments:
        control_num
        total_time_steps
        """
        super().__init__(cost_multiplier=cost_multiplier)
        self.max_control_norms = max_control_norms
        self.diffs_size = control_num * (total_time_steps - order)
        self.order = order
        self.cost_normalization_constant = self.diffs_size * (2 ** self.order)
        self.type="control_explicitly_related"
        self.control_eval_account=total_time_steps

    def cost(self, controls):
        """
        Compute the penalty.

        Arguments:
        controls
        states
        system_eval_step

        Returns:
        cost
        """
        if self.max_control_norms is None:
            normalized_controls = controls

        # Penalize the square of the absolute value of the difference
        # in value of the control parameters from one step to the next.
            diffs = jnp.diff(normalized_controls, axis=0, n=self.order)
            cost = jnp.sum(jnp.real(diffs * jnp.conjugate(diffs)))
        # You can prove that the square of the complex modulus of the difference
        # between two complex values is l.t.e. 2 if the complex modulus
        # of the two complex values is l.t.e. 1 respectively using the
        # triangle inequality. This fact generalizes for higher order differences.
        # Therefore, a factor of 2 should be used to normalize the diffs.
            cost_normalized = cost / self.cost_normalization_constant
        else:
            cost_normalized=0
            diffs = jnp.diff(controls, axis=0, n=self.order)
            for i, max_norm in enumerate(self.max_control_norms):
                diff = diffs[:, i]
                diff_sq = jnp.abs(diff)
                penalty_indices = jnp.nonzero(diff_sq > max_norm)[0]
                penalized_control = diff_sq[penalty_indices]
                penalty = (penalized_control-max_norm)/penalized_control

                penalty_normalized = penalty / (penalty_indices.shape[0]* len(self.max_control_norms))
                cost_normalized = cost_normalized + jnp.sum(penalty_normalized)


        return cost_normalized * self.cost_multiplier

