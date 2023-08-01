import kfp
from kfp import dsl
from kfp.components import create_component_from_func

@create_component_from_func
def print_op(message: str):
    print(message)

@dsl.pipeline(
    name="Kubeflow pipeline parallel example",
    description="Demonstrate the parallel pods of Kubeflow pipeline."
)
def parallelism():
    op1 = print_op("training first model")
    op2 = print_op("training second model")
    dsl.get_pipeline_conf().set_parallelism(2)

if __name__ == "__main__":
    import kfp.compiler as compiler
    compiler.Compiler().compile(parallelism, (__file__ + ".yaml").replace(".py", ""))
