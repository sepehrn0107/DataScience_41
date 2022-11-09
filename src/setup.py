from config import Config

def setup(config: Config):
    from swifter import set_defaults
    
    # Set the swifter defaults.
    # Swifter doc: https://github.com/jmcarpenter2/swifter/blob/master/docs/documentation.md
    set_defaults(
        allow_dask_on_strings=True,
    )