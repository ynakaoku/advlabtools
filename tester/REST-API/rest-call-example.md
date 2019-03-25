### pass JSON file to POST call
curl -X POST -H "Content-Type: application/json" -T tester/k8s-4peers-config.json http://localhost:8000/iperf3/RunTest
