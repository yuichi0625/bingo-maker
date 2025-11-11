import pathlib
import sys


def is_number(s: str):
    try:
        float(s)
        return True
    except ValueError:
        return False


def resolve_resource_path(relative_path: str) -> pathlib.Path:
    base_dir = pathlib.Path(
        getattr(sys, '_MEIPASS', pathlib.Path(__file__).resolve().parents[1])
    )
    return (base_dir / relative_path).resolve()


def resolve_output_path(
    relative_path: str, suffix: str = '.pdf'
) -> pathlib.Path:
    if not relative_path.endswith(suffix):
        relative_path += suffix

    base_dir = (
        pathlib.Path(sys.executable).parent
        if getattr(sys, 'frozen', False)
        else pathlib.Path(__file__).resolve().parent.parent
    )
    output_path = base_dir / relative_path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    return output_path
