# Simple k8s validating admission controller

Simple Python Flask service which validates [Kubernetes deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/):

* **Image Registry Validation** - Validates that the container images being deployed are from the specified image registry 

* **Label Validation** - Validates that the list of labels required by the webhook have been applied to the deployment

## Steps followed to deploy webhook

* [Generated](https://www.digitalocean.com/community/tutorials/openssl-essentials-working-with-ssl-certificates-private-keys-and-csrs) SSL certificates

* Created a new [TLS secret](https://kubernetes.io/docs/concepts/configuration/secret/#tls-secrets) called `webhook-tls` (Refer - [webhook.tls.config.yml](manifests/webhook/webhook.tls.config.yml))

```bash
kubectl create -f manifests/webhook/webhook.tls.config.yml
```

* Deployed the webhook Python Flask service

```bash
kubectl create -f manifests/webhook/webhook.deploy.yml
```

The `IMAGE_REGISTRY` environment variable must be configured to enforce the use of a specific container registry and `LABELS` is a comma separated list of labels that must be added to deployments

* Registered the validating admission controller

```bash
kubectl create -f manifests/webhook/webhook.k8s.validating.config.yml
```

* Tested the webhook by attempting to create the deployments from the `manifests/deployments/` folder

Console output when the correct container registry is not specified:

```
Error from server: error when creating "manifests/deployments/registry-denied.deployment.yml": admission webhook "simple-admission-controller.ashcorp.com" denied the request: select container images from registry - myregistry2022.azurecr.io
```

Console output when the required lables are not added:

```
Error from server: error when creating "manifests/deployments/label-denied.deployment.yml": admission webhook "simple-admission-controller.ashcorp.com" denied the request: labels required are - ['app.kubernetes.io/name', 'environment']
```
