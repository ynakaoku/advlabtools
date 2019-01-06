# advlabtools
Advlabtools is short name of *Advanced Lab Tools* that aims to automating execution of multi point network performance test in virtualized or containerized(kubernetes) environment.  Advlabtools contains programs and definitions for running tests, especially on top of virtual environment like VMware vSphere and NSX environments in terms of deployment automation. In testing function part, the programs will work well in various environment unless the test endpoints are VM or K8s containers.  
The stack can be devided to two major parts: *Deployer* and *Tester*. Deployer is collection of deployment definition examples for various orchestration tools. Tester is collection of test scripts, visualization tools and definition examples for the tools. 

## How it works
### Deployer
Deployer is collection of definitions for orchestration tools like Ansible, Terraform and Kubernetes. The installation of these tools are not included in this package. These definitions can be used to deploy and change test environment automatically without direct interation to components like vSphere, NSX and Kubernetes. 

### Tester
Tester is the most important part of this package. Tester includes bash and python scripts to perform network tests in distributed environment. For example, advlabtools can control multiple VMs and K8s PODs in parallel so that you can test and measure network throughput as aggregation of multiple flows between different, distributed instances. Currently advlabtools works well with iperf3, however apache bench or its descents are partially supported and will be fully supported in future.  
Tester also includes python scripts that can help to visualize test result with Jupyter Notebook. 

## Installation
Basically, you need to provide virtual environment and/or kubernetes environment. 

### For virtual environment

### For Kubernetes environment