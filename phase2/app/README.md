# Task source — Phase 2

Not yet in the repository. The build that writes `SafetyPop2_*` files, with its `Stim/` assets.

Known differences from the Phase 1 source in `../../phase1/app/`:

- Oddity stimuli are two-tone circles, with the target polarity alternating across trials
- 50-trial sessions instead of 60
- No probe trial types
- Three additional output columns: `TargetCellHistory`, `EventLog`, `TrialStart`
- `TargetCellHistory` records the oddity target's cell at every stage, which the Phase 1 source
  did not do
