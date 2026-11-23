"""Command-line interface for a bounded exploratory and held-out experiment."""
import argparse
from .evaluation import run_experiment


def main():
    parser = argparse.ArgumentParser(description="Independent BAAHS-inspired research simulator (not authors' code)")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="Run paired fixed-trajectory experiments")
    run.add_argument("--output", default="results/experiment")
    run.add_argument("--steps", type=int, default=80, help="Events per trajectory; scored visits=steps-1")
    run.add_argument("--seeds-per-batch", type=int, default=50)
    run.add_argument("--max-batches", type=int, default=1)
    run.add_argument("--holdout-seeds", type=int, default=50)
    run.add_argument("--dev-seed-start", type=int, default=0)
    run.add_argument("--holdout-seed-start", type=int, default=1_000_000)
    run.add_argument("--tolerance-pp", type=float, default=1., help="Deviation in percentage points from references")
    run.add_argument("--repeat-until-match", action="store_true", help="Exploratory stopping only; mandatory fresh holdout runs afterward")
    args = parser.parse_args()
    if args.command == "run":
        run_experiment(args.output, steps=args.steps, seeds_per_batch=args.seeds_per_batch,
                       max_batches=args.max_batches, repeat_until_match=args.repeat_until_match,
                       tolerance_pp=args.tolerance_pp, holdout_seeds=args.holdout_seeds,
                       dev_seed_start=args.dev_seed_start,
                       holdout_seed_start=args.holdout_seed_start)


if __name__ == "__main__":
    main()
