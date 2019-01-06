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

