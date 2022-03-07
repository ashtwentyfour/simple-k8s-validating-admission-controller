"""
Simple admission controller
"""
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

def send_response(result, uid, message):
    """Send JSON response"""
    return jsonify({
       "apiVersion": "admission.k8s.io/v1",
       "kind": "AdmissionReview",
       "response": {
          "allowed": result,
          "uid": uid,
          "status": {
             "message": message
          }
        }
    })

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
        message = "select container images " + \
                   "from registry - " + required_registry
        return send_response(False, req["request"]["uid"], message)

    labels = deployment["metadata"]["labels"]
    try:
        required_labels = (os.environ["LABELS"]).split(",")
    except KeyError as err:
        print(f"KeyError: {err}")
    check_labels = validate_labels(labels.keys(), required_labels)
    if not check_labels["status"]:
        message = "labels required are - " + str(required_labels)
        return send_response(False, req["request"]["uid"], message)

    return send_response(True, req["request"]["uid"], "deployment validated")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, \
            ssl_context=('/TLS/tls.crt', \
                         '/TLS/tls.key'))
