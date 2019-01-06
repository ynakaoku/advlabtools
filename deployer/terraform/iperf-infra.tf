# THIS TF FILE IS STILL UNDER DEVELOPMENT
provider "kubernetes" {
  host = "https://192.168.77.134:8443"

  config_context_auth_info = "minikube"
  config_context_cluster   = "minikube"
}

resource "kubernetes_namespace" "terraform" {
  metadata {
    name = "terraform"
  }
}

resource "kubernetes_deployment" "iperf3" {
  metadata {
    name = "iperf3-terraform"
    namespace = "terraform"
    labels {
      App = "iperf3"
    }
  }

  spec {
    replicas = 4

    selector {
      match_labels {
        App = "iperf3"
      }
    }

    template {
      metadata {
        labels {
          App = "iperf3"
        }
      }

      spec { 
        container {
          image = "networkstatic/iperf3"
          command = "['/bin/sh', '-c', 'sleep infinity']"
          name  = "iperf3"

          port {
            container_port = 80
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "nginx" {
  metadata {
    name = "nginx-terraform"
    namespace = "terraform"
  }
  spec {
    selector {
      App = "${kubernetes_pod.nginx.metadata.0.labels.App}"
    }
    port {
      port = 80
      target_port = 80
    }

#    type = "LoadBalancer"
    type = "NodePort"
  }
}

