#  Copyright 2023 kbthu. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import kfp
from kfp import dsl

def create_pv():
  return dsl.VolumeOp(
    name="create_pv",
    resource_name="kfp-pvc",
    size="1Gi",
    modes=dsl.VOLUME_MODE_RWO
  )


def generate_data(vol_name: str):
  cop = dsl.ContainerOp(
    name='generate_data',
    image='bash:5.1',
    command=['sh', '-c'],
    arguments=['echo $(( $RANDOM % 10 + 1 )) | tee /mnt/out.txt']
  )
  cop.container.set_image_pull_policy('IfNotPresent')
  cop.add_pvolumes({'/mnt': dsl.PipelineVolume(pvc=vol_name)})
  return cop


def use_pre_data(vol_name: str):
  cop = dsl.ContainerOp(
    name='use_pre_data',
    image='bash:5.1',
    command=['sh', '-c'],
    arguments=['tail /mnt/out.txt']
  )
  cop.container.set_image_pull_policy('IfNotPresent')
  cop.add_pvolumes({'/mnt': dsl.PipelineVolume(pvc=vol_name)})
  return cop


@dsl.pipeline(
    name="Kubeflow volume example",
    description="Demonstrate the use case of volume on Kubeflow pipeline."
)
def volume_example():
  vop = create_pv()
  cop = generate_data(vop.outputs["name"]).after(vop)
  use_pre_data(vop.outputs["name"]).after(vop,cop)


if __name__ == "__main__":
    import kfp.compiler as compiler
    compiler.Compiler().compile(volume_example, __file__ + ".yaml")