provider "google" {
  project     = "millennia-tech-tree-grapher"
  region      = "us-central1"
}

resource "google_service_account" "grapher" {
  account_id   = "tech-tree-grapher"
  display_name = "Tech tree grapher Service Account"
}

resource "google_cloud_run_v2_service" "default" {
  name     = "tech-tree-grapher"
  location = "us-central1"

  deletion_protection = false # set to "true" in production

  template {
    containers {
      # Replace with the URL of your graphviz image
      #   gcr.io/<YOUR_GCP_PROJECT_ID>/graphviz
      image = "us-docker.pkg.dev/cloudrun/container/hello"
    }

    service_account = google_service_account.grapher.email
  }
}
