"""The ``neptravision`` command-line interface.

A thin Typer shell over the library. Each command does three things: read config,
call one pure library function, print a result. No business logic lives here — that
keeps the science testable without invoking the CLI. Commands are grouped into
sub-apps (``data``, ``annotation``, ``train``, ``eval``, ``analyze``, ``serve``)
mirroring the package structure.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .config import load_classes, load_dataset_config
from .logging_utils import setup_logging
from .paths import PATHS

app = typer.Typer(
    name="neptravision",
    help="Nepal-specific traffic CV benchmark — dataset pipeline, training, evaluation.",
    no_args_is_help=True,
    add_completion=False,
)
data_app = typer.Typer(help="Dataset pipeline: extract → dedup → select → split → convert → stats.")
ann_app = typer.Typer(help="Annotation quality: validate labels, inter-annotator agreement.")
analyze_app = typer.Typer(help="Analysis: Pareto frontier and other paper figures.")
app.add_typer(data_app, name="data")
app.add_typer(ann_app, name="annotation")
app.add_typer(analyze_app, name="analyze")

console = Console()


@app.callback()
def _root(verbose: bool = typer.Option(False, "--verbose", "-v", help="DEBUG logging.")):
    setup_logging("DEBUG" if verbose else None)


@app.command()
def version() -> None:
    """Print the package version."""
    console.print(f"NepTraVision v{__version__}")


@app.command()
def info() -> None:
    """Show the active taxonomy and key paths — a quick sanity check of the setup."""
    classes = load_classes()
    profile = classes.active
    title = f"Active taxonomy: '{classes.active_profile}' ({profile.num_classes} classes)"
    table = Table(title=title)
    table.add_column("id", justify="right")
    table.add_column("name")
    for cid in sorted(profile.names):
        table.add_row(str(cid), profile.names[cid])
    console.print(table)
    console.print(f"[dim]data root:[/dim] {PATHS.data}")
    console.print(f"[dim]experiments:[/dim] {PATHS.experiments}")


# ─────────────────────────────────────────────────────────────────────────────
# data
# ─────────────────────────────────────────────────────────────────────────────
@data_app.command("extract-frames")
def data_extract_frames(
    fps: float = typer.Option(None, help="Frames per second (default from dataset.yaml)."),
    overwrite: bool = typer.Option(False, help="Re-extract even if frames exist."),
) -> None:
    """Extract frames from every video in data/raw_videos/ into data/raw_frames/."""
    from .data import frame_extraction

    cfg = load_dataset_config().extraction
    frame_extraction.extract_all(
        PATHS.raw_videos, PATHS.raw_frames,
        fps=fps if fps is not None else cfg.fps,
        image_format=cfg.image_format, jpg_quality=cfg.jpg_quality, overwrite=overwrite,
    )


@data_app.command("deduplicate")
def data_deduplicate(
    threshold: int = typer.Option(None, help="Hamming distance for 'duplicate'."),
    apply: bool = typer.Option(False, "--apply", help="Move kept frames to data/selected/."),
) -> None:
    """Find near-duplicate frames in data/raw_frames/ (optionally copy survivors)."""
    import shutil

    from .data import deduplicate

    cfg = load_dataset_config().deduplicate
    images = deduplicate.list_images(PATHS.raw_frames)
    result = deduplicate.find_duplicates(
        images, method=cfg.hash, hash_size=cfg.hash_size,
        threshold=threshold if threshold is not None else cfg.threshold,
    )
    console.print(f"Kept [green]{result.n_kept}[/green], dropped [red]{result.n_dropped}[/red].")
    if apply:
        PATHS.ensure(PATHS.selected)
        for img in result.kept:
            shutil.copy2(img, PATHS.selected / img.name)
        console.print(f"Copied {result.n_kept} survivors → {PATHS.selected}")


@data_app.command("select")
def data_select(
    apply: bool = typer.Option(False, "--apply", help="Copy sharp images to data/selected/."),
) -> None:
    """Drop blurry frames from data/selected/ (or data/raw_frames/ if empty)."""
    from .data import deduplicate, select

    cfg = load_dataset_config().select
    source = PATHS.selected if any(PATHS.selected.glob("*")) else PATHS.raw_frames
    images = deduplicate.list_images(source)
    result = select.select_images(images, blur_min_variance=cfg.blur_min_variance)
    console.print(
        f"Kept [green]{result.n_kept}[/green], rejected "
        f"[red]{len(result.rejected_blurry)}[/red] blurry."
    )


@data_app.command("probe-videos")
def data_probe_videos() -> None:
    """Read embedded metadata from data/raw_videos/ into a per-video capture log.

    Auto-fills capture time, GPS, resolution, fps, and device from each file. You then
    open the CSV and fill the columns no camera records: weather and density.
    """
    from .data import capture_log

    PATHS.ensure(PATHS.raw_videos)
    out = capture_log.build_capture_log(PATHS.raw_videos, PATHS.capture_log_csv)
    console.print(
        f"Capture log at {out}\n"
        "[yellow]→ open it and fill the [bold]weather[/bold] and [bold]density[/bold] "
        "columns per clip (location too, if GPS was off).[/yellow]"
    )


@data_app.command("build-manifest")
def data_build_manifest(
    from_capture_log: bool = typer.Option(
        True, help="Inherit per-video conditions from data/raw_videos/capture_log.csv."
    ),
) -> None:
    """Create/update data/dataset/metadata.csv from the selected images.

    By default, each frame inherits its source video's conditions (time/weather/density/
    location/resolution) from the capture log, so you log conditions once per video — not
    once per frame.
    """
    from .data import capture_log, deduplicate, manifest

    images = deduplicate.list_images(PATHS.selected)
    PATHS.ensure(PATHS.dataset)

    source_conditions = None
    if from_capture_log and PATHS.capture_log_csv.is_file():
        source_conditions = capture_log.as_source_conditions(
            capture_log.read(PATHS.capture_log_csv)
        )
        console.print(f"Inheriting conditions from {PATHS.capture_log_csv}.")
    elif from_capture_log:
        console.print(
            "[yellow]No capture log yet — run 'neptravision data probe-videos' first "
            "to auto-fill conditions.[/yellow]"
        )

    manifest.build_template(images, PATHS.metadata_csv, source_conditions)
    console.print(f"Manifest at {PATHS.metadata_csv} — review/complete any blank columns.")


@data_app.command("make-splits")
def data_make_splits() -> None:
    """Compute the leakage-safe train/val/test split from the manifest."""
    from .data import manifest, splits

    cfg = load_dataset_config().split
    records = manifest.read(PATHS.metadata_csv)
    assignment = splits.assign_splits(
        records, ratios=cfg.ratios, group_by=cfg.group_by,
        stratify_by=cfg.stratify_by, seed=cfg.seed,
    )
    splits.write_split_definition(assignment, PATHS.dataset_splits)


@data_app.command("write-data-yaml")
def data_write_data_yaml() -> None:
    """Write the Ultralytics data.yaml for the active taxonomy."""
    from .data import convert

    profile = load_classes().active
    out = convert.write_ultralytics_data_yaml(
        profile, PATHS.dataset, PATHS.dataset / "data.yaml"
    )
    console.print(f"Wrote {out}")


@data_app.command("stats")
def data_stats() -> None:
    """Print class distribution and counts over data/dataset/labels/."""
    from .data import stats

    profile = load_classes().active
    s = stats.compute_label_stats(PATHS.dataset_labels, profile)
    table = Table(title=f"Dataset stats — {s.n_images} images, {s.n_boxes} boxes")
    table.add_column("class")
    table.add_column("instances", justify="right")
    for name, count in s.class_counts.items():
        table.add_row(name, str(count))
    console.print(table)


# ─────────────────────────────────────────────────────────────────────────────
# annotation
# ─────────────────────────────────────────────────────────────────────────────
@ann_app.command("validate")
def annotation_validate(
    labels_dir: Path = typer.Argument(None, help="Defaults to data/dataset/labels."),
    images_dir: Path = typer.Option(None, help="Cross-check image↔label correspondence."),
) -> None:
    """Validate YOLO label files against the frozen taxonomy."""
    from .annotation import validate

    profile = load_classes().active
    report = validate.validate_labels(labels_dir or PATHS.dataset_labels, profile, images_dir)
    console.print(report.summary())
    for err in report.errors[:50]:
        console.print(f"[red]✗[/red] {err}")
    raise typer.Exit(code=0 if report.ok else 1)


@ann_app.command("agreement")
def annotation_agreement(
    labels_a: Path = typer.Argument(..., help="First annotator's label dir."),
    labels_b: Path = typer.Argument(..., help="Second annotator's label dir."),
    iou: float = typer.Option(0.5, help="IoU threshold for matching boxes."),
) -> None:
    """Inter-annotator agreement (mean IoU + class agreement) on the shared subset."""
    from .annotation import agreement

    result = agreement.compute_agreement(labels_a, labels_b, iou_thr=iou)
    console.print(result.summary())


# ─────────────────────────────────────────────────────────────────────────────
# train / eval / serve (thin dispatchers into the heavy modules)
# ─────────────────────────────────────────────────────────────────────────────
@app.command("train")
def train(
    model: str = typer.Option(..., help="Model name, e.g. yolov8n (see configs/models/)."),
    seed: int = typer.Option(0, help="Random seed."),
    imgsz: int = typer.Option(None, help="Override input size (320/416/640)."),
) -> None:
    """Fine-tune one model on the dataset. Requires the [train] extra."""
    from .training.train import train_one

    data_yaml = PATHS.dataset / "data.yaml"
    run = train_one(model, data_yaml, seed=seed, imgsz=imgsz)
    console.print(f"Done. Run dir: {run.dir}")


@app.command("benchmark")
def benchmark(
    experiment: str = typer.Option(..., help="Experiment id, e.g. e1_baselines."),
    dry_run: bool = typer.Option(
        False, "--dry-run",
        help="Simulate metrics (no torch/data) to validate the pipeline and produce demo tables.",
    ),
) -> None:
    """Run an experiment config → result tables in results/tables/.

    Use --dry-run to exercise the full flow without training; drop it (and install the
    [train] extra + build the dataset) for real numbers.
    """
    from .benchmark.runner import run_benchmark

    data_yaml = PATHS.dataset / "data.yaml"
    result = run_benchmark(
        experiment, dry_run=dry_run,
        data_yaml=data_yaml if data_yaml.is_file() else None,
    )
    if result.dry_run:
        console.print("[yellow]⚠ Simulated numbers (simulated=true) — demo/testing only.[/yellow]")
    console.print(f"Accuracy table → {result.accuracy_table}")
    if result.efficiency_table:
        console.print(f"Efficiency table → {result.efficiency_table}")


@app.command("eval")
def eval_model(
    model: str = typer.Option(..., help="Model name (for labelling the result)."),
    weights: Path = typer.Option(..., help="Trained .pt checkpoint to evaluate."),
    split: str = typer.Option("test", help="Dataset split to evaluate on."),
    imgsz: int = typer.Option(640, help="Evaluation input size."),
) -> None:
    """Evaluate a trained checkpoint on a split. Requires the [train] extra."""
    from .evaluation.metrics import evaluate_ultralytics

    data_yaml = PATHS.dataset / "data.yaml"
    metrics = evaluate_ultralytics(weights, data_yaml, model_name=model, split=split, imgsz=imgsz)
    console.print(
        f"[bold]{model}[/bold]  mAP50={metrics.map50:.3f}  mAP50-95={metrics.map50_95:.3f}  "
        f"P={metrics.precision:.3f}  R={metrics.recall:.3f}  F1={metrics.f1:.3f}"
    )


@analyze_app.command("pareto")
def analyze_pareto(
    experiment: str = typer.Option("e2_efficiency", help="Experiment id whose tables to read."),
    tier: str = typer.Option(None, help="Hardware tier to plot (default: all tiers in the table)."),
) -> None:
    """Plot the accuracy-vs-FPS Pareto frontier per hardware tier → results/figures/."""
    from .analysis.pareto import load_pareto_points, plot_pareto
    from .benchmark.tables import read_table

    acc_csv = PATHS.results_tables / f"{experiment}_accuracy.csv"
    eff_csv = PATHS.results_tables / f"{experiment}_efficiency.csv"
    for path in (acc_csv, eff_csv):
        if not path.is_file():
            raise typer.BadParameter(
                f"Missing {path.name}. Run the benchmark for '{experiment}' first."
            )

    tiers = [tier] if tier else sorted({r["hardware_tier"] for r in read_table(eff_csv)})
    for t in tiers:
        points = load_pareto_points(acc_csv, eff_csv, t)
        if not points:
            console.print(f"[yellow]No points for tier '{t}'.[/yellow]")
            continue
        out = PATHS.results_figures / f"pareto_{experiment}_{t}.png"
        plot_pareto(points, out, title=f"Accuracy vs. FPS — {t}", xlabel="FPS", ylabel="mAP@0.5")
        console.print(f"Pareto figure ({t}) → {out}")


@app.command("serve")
def serve(
    host: str = typer.Option("127.0.0.1"),
    port: int = typer.Option(8000),
    weights: Path = typer.Option(None, help="Trained .pt; omit to use the mock detector."),
) -> None:
    """Launch the prototype dashboard. Requires the [serve] extra."""
    try:
        import uvicorn
    except ImportError as exc:
        raise typer.BadParameter('serve extra not installed: pip install -e ".[serve]"') from exc

    from .prototype.app import create_app
    from .prototype.inference import MockDetector, UltralyticsDetector

    detector = UltralyticsDetector(weights) if weights else MockDetector()
    uvicorn.run(create_app(detector), host=host, port=port)


if __name__ == "__main__":
    app()
