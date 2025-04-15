
import kfp
from kfp import dsl

def create_pv():
  return dsl.VolumeOp(
    name="create_pv",
    resource_name="kfp-pvc",
    size="1Gi",
    modes=dsl.VOLUME_MODE_RWO
  )


def parallel_1(vol_name: str):
  cop = dsl.ContainerOp(
    name='generate_data',
    image='bash:5.1',
    command=['sh', '-c'],
    arguments=['echo 1 | tee /mnt/out1.txt']
  )
  cop.container.set_image_pull_policy('IfNotPresent')
  cop.add_pvolumes({'/mnt': dsl.PipelineVolume(pvc=vol_name)})
  return cop


def parallel_2(vol_name: str):
  cop = dsl.ContainerOp(
    name='generate_data',
    image='bash:5.1',
    command=['sh', '-c'],
    arguments=['echo 2 | tee /mnt/out2.txt']
  )
  cop.container.set_image_pull_policy('IfNotPresent')
  cop.add_pvolumes({'/mnt': dsl.PipelineVolume(pvc=vol_name)})
  return cop


def parallel_3(vol_name: str):
  cop = dsl.ContainerOp(
    name='generate_data',
    image='bash:5.1',
    command=['sh', '-c'],
    arguments=['echo 3 | tee /mnt/out3.txt']
  )
  cop.container.set_image_pull_policy('IfNotPresent')
  cop.add_pvolumes({'/mnt': dsl.PipelineVolume(pvc=vol_name)})
  return cop


@dsl.pipeline(
    name="Kubeflow volume parallel example",
    description="Demonstrate the use case of volume on Kubeflow pipeline.")
def volume_parallel():
    vop = create_pv()
    cop1 = parallel_1(vop.outputs["name"]).after(vop)
    cop2 = parallel_2(vop.outputs["name"]).after(vop)
    cop3 = parallel_3(vop.outputs["name"]).after(vop)


if __name__ == "__main__":
    import kfp.compiler as compiler
    compiler.Compiler().compile(volume_parallel, __file__ + ".yaml")