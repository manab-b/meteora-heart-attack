# Walk-forward validation

Parameter selection is now separated from evaluation.

1. Split each bin configuration into train/test observations.
2. Run the parameter grid only on train.
3. Select the best train configuration.
4. Evaluate that exact configuration on unseen test observations.
5. Compare train/test fee velocity and exit behavior.

This prevents choosing Heart Attack parameters from the same observations used to judge them.
