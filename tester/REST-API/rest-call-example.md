### pass JSON file to POST call
curl -X POST -H "Content-Type: application/json" -T ../k8s-2peers-1ns-config.json http://localhost:8000/iperf3/RunTest

### RunTest
curl -X POST -H "Content-Type: application/json" -T ../k8s-2peers-2ns-config.json http://localhost:8000/iperf3/RunTest

### GetHistory
curl -X GET  -H "Content-Type: application/json"  http://localhost:8000/iperf3/GetTestHistory

### GetTestDetails
curl -X GET  -H "Content-Type: application/json"  http://localhost:8000/iperf3/GetTestDetails?testid=K8s-test01-iperf3-190331-230239


