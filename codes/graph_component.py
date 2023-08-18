from kfp import components, dsl

@components.func_to_container_op
def task_op() -> int:
  from random import randint
  return randint(1, 10)


@components.func_to_container_op
def print_op(message: str):
  print(message)

	
@dsl.graph_component
def train_loop(input: int):
  with dsl.Condition(input >= 6):
    print_op('final: ' + str(input))
	
  with dsl.Condition(input < 6):
    op = task_op()
    train_loop(op.output)


@dsl.pipeline()
def my_pipeline():
  op = task_op()
  tr_op = train_loop(op.output)
  tr_op.after(op)


if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(my_pipeline, (__file__ + '.yaml').replace('.py', ''))