import os


def plot_path(city: str, name: str) -> str:
    # This is run from src
    path = f"../plots/{city}/{name}.svg".lower().replace(" ", "_")

    if "." not in path:
        path += ".svg"

    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    return path
