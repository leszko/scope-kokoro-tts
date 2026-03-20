from scope.core.plugins import hookimpl


@hookimpl
def register_pipelines(register):
    from .pipeline import KokoroTTSPipeline

    register(KokoroTTSPipeline)
