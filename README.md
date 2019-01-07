# advlabtools
*Advlabtools* is short name of *Advanced Lab Tools* that aims to automating execution of multi point network performance test in virtualized or containerized(kubernetes) environment.  Advlabtools contains programs and definitions for running tests, especially on top of virtual environment like VMware vSphere and NSX environments in terms of deployment automation. In testing function part, the programs will work well in various environment unless the test endpoints are VM or K8s containers.  
The stack can be devided to two major parts: *Deployer* and *Tester*. Deployer is collection of deployment definition examples for various orchestration tools. Tester is collection of test scripts, visualization tools and definition examples for the tools. 

## How it works
### Deployer
Deployer is collection of definitions for orchestration tools like Ansible, Terraform and Kubernetes. The installation of these tools are not included in this package. These definitions can be used to deploy and change test environment automatically without direct interation to components like vSphere, NSX and Kubernetes. 

### Tester
Tester is the most important part of this package. Tester includes bash and python scripts to perform network tests in distributed environment. For example, advlabtools can control multiple VMs and K8s PODs in parallel so that you can test and measure network throughput as aggregation of multiple flows between different, distributed instances. Currently advlabtools works well with iperf3, however apache bench or its descents are partially supported and will be fully supported in future.  
Tester also includes python scripts that can help to visualize test result with Jupyter Notebook. 

## Installation and Setup
Basically, you need to provide at least 1 controller machine as well as virtual machines and/or kubernetes deployments as test instances.   
### Setup Controller Machine
Please select your favorite form factor for advlabtools controller machine. In case that you selected Linux or MacOSX machine as controller, please follow these steps.  
#### Python Installation
At first, please ensure that these packages are installed in your controller machine: 
- python 2.7
- python modules
  - python-devel
  - pip
  - gcc
  - tk-devel
  - numpy
  - matplotlib
  - subprocess
  - json
  - PyYAML
  - jupyter
  - kubernetes

#### advlabtools Installation
Next, please clone the *advlabtools* package from GitHub into your controller as below:
```
$ git clone https://github.com/ynakaoku/advlabtools.git
```
In the `advlabtools` directory, `deployer` and `tester` directories exists. 
```
$ cd advlabtools
$ ls
deployer  README.md  tester
```
In `tester` directory, examples of test definition, as well as bash and python scripts for test automation and visualization can be found much like below:
```
$ cd tester
$ ls
DLS1-config             ESG4-config             NP3-L2VPN.config        reports
DLS2-config             ESG4a-config            all-targets-config      scripts
DLS4-config             NP1-ESG.config          jupyter
ESG2-config             NP2-DLR.config          k8s-4peers-config.yaml
$ ls scripts
authorize_esx.bash              optlib                          run_ping_test.bash
authorize_tester.bash           run_abench_cl.bash              servers_status.bash
authorize_tester_old.bash       run_iperf3_cl.bash              start_servers.bash
k8s_iperf3_peer.bash            run_iperf3_peer.bash            stop_esxtop.bash
k8s_servers_status.bash         run_iperf_cl.bash               stop_servers.bash
k8s_stop_servers.bash           run_iperf_peer.bash
$ ls jupyter
DefaultTestPage.ipynb   abench_cl.py            k8s-iperf-test.ipynb    reports
abench.ipynb            iperf3_peer.py          k8s_iperf3_peer.py      start-jupyter.sh
```
`scripts` directory holds several bash scripts that initialize test environment and perform automatic test against target VMs and/or Kubernetes PODs.  
`jupyter` directory stores sample test contents for Jupyter Notebook. From the contents you can execute python scripts held in this directory to automatically run test and visualize the results with Python modules.  
If you would like to run bash scripts from `tester` directory, please add the path to `scripts` into your $PATH environment variable:
```
$ PATH=$PATH:./scripts
```

### Setup Virtual Machines  
#### Providing VM Image and Install Test Tools  
If you would like to perform test against VMs, you need to setup VMs with Linux OS, and install test tools that *advlabtools* will utilize. 
- iperf2 and iperf3  
- ab (Apache Bench)  
- httpd (Apache Httpd), etc. 

Creating golden image for test VM is recommended.  

#### Setup Network Interfaces  
Also, network interfaces of the VMs must be correctly configured following manners below: 
- Target port (or testip port) must be `ens160`  
- Server management port must be `ens192`  

#### Setup vSphere Hypervisors (optional) 
In vSphere environment, *advlabtools* can collect performance data of ESXi servers via ESXTOP command. Please enable ESXi shell and permit ssh login. 

#### Create Environment Definition for Initializing Test VMs
In `tester` directory, some examples of test definition are available. Please make your copy and update the VMs IP addresses for your test scenario.
```
$ more all-targets-config
servers=("172.16.130.201" "172.16.130.202" "172.16.130.203" "172.16.130.204" "172.16.130.205" "172.16.130.206" "172.16.130.207" "172.16.130.208")
hosts=("172.16.130.4" "172.16.130.5" "172.16.130.6" "172.16.130.7")
mode="iperf"
proto="tcp"
```
This is shell variable type definition. Please fill `servers` variable with resolvable hostname or IP address assigned to management port of your test VMs. Also, please fill `hosts` variable with hostname or address of your ESXi hypervisors. `mode` and `proto` are not effective in this step.  

#### Authorize VMs
To accept the ssh login from controller to test VMs automatically, distribute authorization keys to VMs beforehand. 
```
$ authorize_tester.bash -C all-targets-config
Generating public/private rsa key pair.
Enter file in which to save the key (/home/ynakaoku/.ssh/id_rsa): <empty>
Created directory '/home/ynakaoku/.ssh'.
Enter passphrase (empty for no passphrase): <empty>
Enter same passphrase again: <empty>
Your identification has been saved in /home/ynakaoku/.ssh/id_rsa.
Your public key has been saved in /home/ynakaoku/.ssh/id_rsa.pub.
The key fingerprint is:
SHA256:YBUUaFUZ8HK11OES8D3WNM9TFNfYAGhajVAbvrb83uA ynakaoku@localhost.localdomain
The key's randomart image is:
+---[RSA 2048]----+
|       +OB*B=ooOB|
|      o. o**.=o+B|
|     .o .+= + =.+|
|     . ..o . o ..|
|        S o      |
|         o .     |
|          o .    |
（続き）
|           o o   |
|           .E .  |
+----[SHA256]-----+
copy public key to VM 172.16.130.202...
The authenticity of host '172.16.130.202 (172.16.130.202)' can't be established.
ECDSA key fingerprint is SHA256:jtFPotTJkiw/KcMxOJgFrXP11ja4cpkzSg9BeKgNVGA.
ECDSA key fingerprint is MD5:3e:1a:52:75:db:83:51:2e:5a:40:70:c8:1c:f5:a9:58.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '172.16.130.202' (ECDSA) to the list of known hosts.
root@172.16.130.202‘s password: <input root password of the test VM>
id_rsa.pub                                    100%  412   308.4KB/s   00:00
...
(Note: repeatably copy public key to all VMs defined in config file)
...
activating public key on VM 172.16.130.202...
root@172.16.130.202's password: <input root password of the test VM>
...
(Note: repeatably activate public key of all VMs)
...
$
```
#### Authorize ESXi Hypervisors
To accept the ssh login from controller to ESXi hypervisors automatically, distribute authorization keys to VMs beforehand. 
```
$ authorize_esxi.bash -C all-targets-config
...
```

### Setup Kubernetes Deployments
#### Providing Kubernetes YAML file 
If you would like to perform test aganst Kubernetes containers, please write YAML definition for Deployments and Services. Below is typical definition for single pair of Deployment and Service optimized for use with *advlabtools*.   
Examples of YAML definition are in `deployer/kubernetes` directory.
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: iperf3-dep1
  labels:
    app: iperf3
spec:
  replicas: 1
  selector:
    matchLabels:
      app: iperf3
  template:
    metadata:
      labels:
        app: iperf3
    spec:
      hostname: iperf3-dep1
      affinity:
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 1
            preference:
              matchExpressions:
              - key: kubernetes.io/role
                operator: In
                values:
                - master
      tolerations:
        - key: node-role.kubernetes.io/master
          operator: Exists
          effect: NoSchedule
      containers:
      - name: iperf3
        image: networkstatic/iperf3
        command: ['/bin/sh', '-c', 'sleep infinity']
        # To benchmark manually: kubectl exec iperf3-clients-jlfxq -- /bin/sh -c 'iperf3 -c iperf3-server'
        ports:
        - containerPort: 5201
          name: iperf3-dep1
      terminationGracePeriodSeconds: 0

---

apiVersion: v1
kind: Service
metadata:
  name: iperf3-dep1
spec:
  selector:
    app: iperf3
  ports:
  - protocol: TCP
    port: 5201
    targetPort: iperf3-dep1

---
```
Key points of YAML definition are below:
- `metadata.name`: unique name for the Deployment or the Services.  
- `metadata.labels`: label `app=iperf3` is used to identify type of Deployments and Services.  
- `spec.replicas`: number of Deployment instance PODs. This must be `1` always because *advlabtools* treats the Deployment as single endpoint for test.  
- `spec.selector`: label `app=iperf3` is used to identify type of Deployments and Services.    
- `spec.template.spec.hostname`: unique hostname of the Deployment. This value must be same to `metadata.name` of the Deployment and the Service so that *advlabtools* can correlate Deployment and Service even after UUID is allocated and assigned to `metadata.name` of the Deployment after PODs creation. For example, if given name for a Deployment/POD is `iperf3-dep1`, `spec.template.spec.hostname` of the POD and `metadata.name` of correlated Service must be `iperf3-dep1`. 
- `sepc.template.spec.containers.image`: Container image that will be copied to container in instantiation. The image includes test tools like `iperf3` that will be used to run performance test from *advlabtools*. 
- `sepc.template.spec.containers.command`: The Deployment should run `sh` infinitely to prevent Kubernetes suspend it for inactivity. 
- `sepc.template.spec.containers.ports`: `containerPorts` should be port number that will be utilized by test tools. `name` must be unique id so that the Deployment and the Service are correlated certainly. Usualy it should be same to `metadata.name`. 

#### Start and Stop Deployments
To start the Deployments and Services:
```
$ kubectl create -f <YAML file>
```
This command just create the Deployments/PODs but test tools are not.  
To stop the Deployments and Services:
```
$ kubectl delete -f <YAML file>
```

### Setup Jupyter Notebook  
The most effective way to test and analyze the result with *advlabtools* is to use Python scripts from Jupyter Notebook. To setup Jupyter Notebook, please follow the steps below:
```
$ jupyter notebook --generate-config
Writing default config to: /home/{login_name}/.jupyter_notebook_config.pu
$ jupyter notebook password
Enter password:
Verify password: 
[NotebookPasswordApp] Wrote hashed password to /home/{login_name}/.jupyter/jupyter_notebook_config.py
$
```
To start your Jupyter Notebook session, please move to `jupyter` directory and run:
```
$ cd ~/advlabtools/tester/jupyter
$ jupyter notebook --ip={IP address of this server} --port={your port number}
[I 17:53:30.138 NotebookApp] Serving notebooks from local directory: /home/{login name}
[I 17:53:30.138 NotebookApp] 0 active kernels
[I 17:53:30.138 NotebookApp] The Jupyter Notebook is running at:
[I 17:53:30.138 NotebookApp] http://{IP address}:{Port number}/
[I 17:53:30.138 NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
[W 17:53:30.139 NotebookApp] No web browser found: could not locate runnable browser.
```
Once the Jupyter Notebook started, please access to `http://{IP address}:{port number}/`.   
To stop Jupyter Notebook, punch `Ctrl-C` at shell session. 

## Testing
### Run Test from Jupyter Notebook
#### Create Test Scenario  
*advlabtools* currently supports two types of test scenario definition; one is shell variable based and another is YAML based. Here I would describe YAML based definition.  
Below is example scenario of 4 test flows between 8 K8s PODs. 
```
flows:
  - server:
      name: iperf3-dep1
      type: kubernetes
    client:
      name: iperf3-dep5
      type: kubernetes
    target: iperf3-dep1

  - server:
      name: iperf3-dep2
      type: kubernetes
    client:
      name: iperf3-dep6
      type: kubernetes
    target: iperf3-dep2

  - server:
      name: iperf3-dep3
      type: kubernetes
    client:
      name: iperf3-dep7
      type: kubernetes
    target: iperf3-dep3

  - server:
      name: iperf3-dep4
      type: kubernetes
    client:
      name: iperf3-dep8
      type: kubernetes
    target: iperf3-dep4

mode: iperf3
proto: tcp
```
Descriptions:
- `flows`: Definitions of test flows. One flow consists of `server`, `client` and `target`. 
  - `server`: definition of server. `name` should be name or IP address of one test instance already deployed and running. When `type` is `kubernetes`, the program will treat the instance as K8s POD. Otherwise it will be treated as VM. 
  - `client`: definition of client. Meaning of `name` and `type` items are same to `server` at all.  
  - `target`: definition of target for test. Client instance will send generated test traffic to this resolvable name or IP address. In case of Kubernetes PODs, the name of the instance must be resolvable by Kubernetes.  
- `mode`: definition of test tool that will be used for this scenario. 
- `proto`: definition of protocol that will be used for this scenario. 

#### Execute Test Scenario
To run your created scenario from Jupyter Notebook, please open a Notebook from UI and fill a command box with the script name and variables like this: 
```
%run -i k8s_iperf3_peer.py -C k8s-4peers-config.yaml -N k8s-4peers -t 10 -b 1G
```
This command will read YAML scenario file in `tester` directory, and create temporary scenario definition file as `/tmp/advlabtools-scenario-temp`. This temp file is scenario file with shell variable format. Actual test is executed by bash script based on the temporary scenario, and result will be captured by Python program after the execution. Collected data will be analized and traffic graph will be generated in Jupyter Notebook UI.  
The script can generated help messages if you need:
```
%run -i k8s_iperf3_peer.py -h
```

### Run Test with Bash Scripts
TBD

## Contact
For any suggestion, request and report, please contact to ynakaoku@vmware.com.
