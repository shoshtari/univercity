from IPython import embed

from common.configs import load_settings
from common.initialize import init_dependency


def shell() -> None:
    settings = load_settings()
    deps = init_dependency(settings)
    for key in deps.__dict__.keys():
        exec(f"{key} = deps.{key}")

    embed(colors="linux")  # type: ignore[no-untyped-call]
