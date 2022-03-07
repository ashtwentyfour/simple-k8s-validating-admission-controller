"""
Simple admission controller
"""
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

def validate_images(containers, required_registry):
    """Validates container image registries"""
    for container in containers:
        if not container["image"].startswith(required_registry):
            return False
    return True

def validate_labels(labels, required_labels):
    """Checks for required labels"""
    for label in required_labels:
        if label not in labels:
            return {
               "status": False, "missing_label": label
            }
    return {
       "status": True
    }

@app.route('/health/ready')
def health():
    """Health check"""
    return jsonify({"status": "UP"})

@app.route('/validate-deploy', methods=['POST'])
def validate_deployment():
    """k8s Deployment validation"""
    req = request.get_json()
    deployment = req["request"]["object"]

    try:
        required_registry = os.environ["IMAGE_REGISTRY"]
    except KeyError as err:
        print(f"KeyError: {err}")

    containers = deployment["spec"]["template"]["spec"]["containers"]
    if not validate_images(containers, required_registry):
        return jsonify({
           "apiVersion": "admission.k8s.io/v1",
           "kind": "AdmissionReview",
           "response": {
              "allowed": False,
              "uid": req["request"]["uid"],
              "status": {
                 "message": "select container images " + \
                           "from registry => " + required_registry
              }
           }
        })

    labels = deployment["metadata"]["labels"]
    try:
        required_labels = (os.environ["LABELS"]).split(",")
    except KeyError as err:
        print(f"KeyError: {err}")
    check_labels = validate_labels(labels.keys(), required_labels)
    if not check_labels["status"]:
        return jsonify({
           "apiVersion": "admission.k8s.io/v1",
           "kind": "AdmissionReview",
           "response": {
              "allowed": False,
              "uid": req["request"]["uid"],
              "status": {
                 "message": check_labels["missing_label"] + " label not set"
              }
           }
        })

    return jsonify({
       "apiVersion": "admission.k8s.io/v1",
       "kind": "AdmissionReview",
       "response": {
          "allowed": True,
          "uid": req["request"]["uid"],
          "status": {
             "message": "deployment validated"
          }
       }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, \
            ssl_context=('/TLS/tls.crt', \
                         '/TLS/tls.key'))
