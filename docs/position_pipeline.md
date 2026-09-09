# Position pipeline

A position snapshot is now a first-class object.

For each observation:
- identify the position
- identify owner and pool
- record lower/upper bins
- record deposited token amounts
- record unclaimed fees
- calculate fee deltas between observations

This is intentionally separate from pool-wide volume. A pool can have high volume while a particular LP position earns little or nothing.

The next adapter should consume an authoritative Meteora position representation and normalize it into PositionSnapshot. Only after that normalization should PaperEngine receive fee deltas.
