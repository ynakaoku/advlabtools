# How to define and operate K8s Deployments and Services for advlabtools

## Node  
Kubernetes Deployment uses `spec.template.spec.nodeSelector` to identify target k8s node so that test target nodes can be set as required.  
Please run command like below before creating test Deployments and Services to add label to the target nodes:
`kubectl label nodes minikube id=node1`
 
## Deployment
Deployment will use `spec.template.spec.hostname` as identifier for unique instance. This item must be equal to instance name so that programs can recognize instances uniquely even after UUID is allocated to instances.

## Service
TBD  

### Create deployment and service
`kubectl create -f <yaml file>`  

### Delete deployment and service
`kubectl delete -f <yaml file>`

