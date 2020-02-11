"""Some utilities for working with Kubernetes.

TODO: These should probably be replaced by functions in fairing.
"""

def apply_k8s_specs(specs):
    """Run apply on the provided Kubernetes specs.
    
    Args:
      specs: A list of strings or dicts providing the YAML specs to
        apply.
    """
    
    # Create the virtual service
    VS_GROUP = "networking.istio.io"
    VS_VERSION = "v1alpha3"
    VS_PLURAL = "virtualservices"

    try:
        vs = crds.create_namespaced_custom_object(
                VS_GROUP,
                VS_VERSION,
                namespace,
                VS_PLURAL,
                yaml.load(ui_virtual_service))

    except k8s_rest.ApiException as e:
        if e.status == 409:
            logging.warning(f"Virtual service {ui_name} already exists")
        else:
            raise
    