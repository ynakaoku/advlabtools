# How to define and operate K8s Deployments and Services for advlabtools

## Deployment
Deployment will use `spec.template.spec.hostname` as identifier for unique instance. This item must be equal to instance name so that programs can recognize instances uniquely even after UUID is allocated to instances.

## Service
TBD  

### Create deployment and service
`kubectl create -f <yaml file>`  

### Delete deployment and service
`kubectl delete -f <yaml file>`

