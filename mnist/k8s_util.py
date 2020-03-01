"""Some utilities for working with Kubernetes.

TODO: These should probably be replaced by functions in fairing.
"""
import logging
import re
import yaml

from kubernetes import client as k8s_client
from kubernetes.client import rest as k8s_rest

def camel_to_snake(name):
  name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
  return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

K8S_CREATE = "K8S_CREATE"
K8S_REPLACE = "K8S_REPLACE"
K8S_CREATE_OR_REPLACE = "K8S_CREATE_OR_REPLACE"

def _get_result_name(result):
  # For custom objects the result is a dict but for other objects
  # its a python class
  if isinstance(result, dict):
    result_name = result["metadata"]["name"]
    result_namespace = result["metadata"]["name"]
  else:
    result_name = result.metadata.name
    result_namespace = result.metadata.namespace

  return result_namespace, result_name

def apply_k8s_specs(specs, mode=K8S_CREATE): # pylint: disable=too-many-branches,too-many-statements
  """Run apply on the provided Kubernetes specs.

  Args:
    specs: A list of strings or dicts providing the YAML specs to
      apply.

    mode: (Optional): Mode indicates how the resources should be created.
      K8S_CREATE - Use the create verb. Works with generateName
      K8S_REPLACE - Issue a delete of existing resources before doing a create
      K8s_CREATE_OR_REPLACE - Try to create an object; if it already exists
        replace it
  """
  # TODO(jlewi): How should we handle patching existing updates?

  results = []

  if mode not in [K8S_CREATE, K8S_CREATE_OR_REPLACE, K8S_REPLACE]:
    raise ValueError(f"Unknown mode {mode}")

  for s in specs:
    spec = s
    if not isinstance(spec, dict):
      spec = yaml.load(spec)

    name = spec["metadata"]["name"]
    namespace = spec["metadata"]["namespace"]
    kind = spec["kind"]
    kind_snake = camel_to_snake(kind)

    plural = spec["kind"].lower() + "s"

    result = None
    if not "/" in spec["apiVersion"]:
      group = None

    else:
      group, version = spec["apiVersion"].split("/", 1)

    if group is None or group.lower() == "apps":
      if group is None:
        api = k8s_client.CoreV1Api()
      else:
        api = k8s_client.AppsV1Api()

      create_method_name = f"create_namespaced_{kind_snake}"
      create_method_args = [namespace, spec]

      replace_method_name = f"delete_namespaced_{kind_snake}"
      replace_method_args = [name, namespace]

    else:
      api = k8s_client.CustomObjectsApi()

      create_method_name = f"create_namespaced_custom_object"
      create_method = getattr(api, create_method_name)
      create_method_args = [group, version, namespace, plural, spec]

      delete_options = k8s_client.V1DeleteOptions()
      replace_method_name = f"delete_namespaced_custom_object"
      replace_method_args = [group, version, namespace, plural, name, delete_options]

    create_method = getattr(api, create_method_name)
    replace_method = getattr(api, replace_method_name)

    if mode in [K8S_CREATE, K8S_CREATE_OR_REPLACE]:
      try:
        result = create_method(*create_method_args)
        result_namespace, result_name = _get_result_name(result)
        logging.info(f"Created {kind} {result_namespace}.{result_name}")
        results.append(result)
        continue
      except k8s_rest.ApiException as e:
        # 409 is conflict indicates resource already exists
        if e.status == 409 and mode == K8S_CREATE_OR_REPLACE:
          pass
        else:
          raise

    # Using replace didn't work for virtualservices so we explicitly delete
    # and then issue a create
    result = replace_method(*replace_method_args)
    logging.info(f"Deleted {kind} {namespace}.{name}")

    result = create_method(*create_method_args)
    result_namespace, result_name = _get_result_name(result)
    logging.info(f"Created {kind} {result_namespace}.{result_name}")
    # Now recreate it
    results.append(result)

  return results

def get_iap_endpoint():
  """Return the URL of the IAP endpoint"""
  extensions = k8s_client.ExtensionsV1beta1Api()
  kf_ingress = None

  try:
    kf_ingress = extensions.read_namespaced_ingress("envoy-ingress", "istio-system")
  except k8s_rest.ApiException as e:
    if e.status == 403:
      logging.warning(f"The service account doesn't have sufficient privileges "
                      f"to get the istio-system ingress. "
                      f"You will have to manually enter the Kubeflow endpoint. "
                      f"To make this function work ask someone with cluster "
                      f"priveleges to create an appropriate "
                      f"clusterrolebinding by running a command.\n"
                      f"kubectl create --namespace=istio-system rolebinding "
                       "--clusterrole=kubeflow-view "
                       "--serviceaccount=${NAMESPACE}:default-editor "
                       "${NAMESPACE}-istio-view")
      return ""

    raise

  return f"https://{kf_ingress.spec.rules[0].host}"

## Use by AWS
def get_ingress_endpoint():
  """Return the URL of the Ingress endpoint"""
  extensions = k8s_client.ExtensionsV1beta1Api()
  kf_ingress = None

  try:
    kf_ingress = extensions.read_namespaced_ingress("istio-ingress", "istio-system")
  except k8s_rest.ApiException as e:
    if e.status == 403:
      logging.warning(f"The service account doesn't have sufficient privileges "
                      f"to get the istio-system ingress. "
                      f"You will have to manually enter the Kubeflow endpoint. "
                      f"To make this function work ask someone with cluster "
                      f"priveleges to create an appropriate "
                      f"clusterrolebinding by running a command.\n"
                      f"kubectl create --namespace=istio-system rolebinding "
                       "--clusterrole=kubeflow-view "
                       "--serviceaccount=${NAMESPACE}:default-editor "
                       "${NAMESPACE}-istio-view")
      return ""

    raise

  return f"http://{kf_ingress.status.load_balancer.ingress[0].hostname}"