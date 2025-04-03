provider "google" {
  project     = var.project
  region      = "us-central1"
}

resource "google_service_account" "grapher" {
  account_id   = "tree-grapher"
  display_name = "Tech tree grapher Service Account"

  create_ignore_already_exists = true
}

resource "google_cloud_run_v2_service" "default" {
  name     = "tech-tree-grapher"
  location = "us-central1"

  deletion_protection = false # set to "true" in production

  template {
    containers {
      image = "gcr.io/millennia-tech-tree-grapher/github.com/millennia"
    }

    service_account = google_service_account.grapher.email
  }
}

resource "google_cloud_run_service_iam_member" "allow_unauthenticated" {
  service  = google_cloud_run_v2_service.default.name
  location = google_cloud_run_v2_service.default.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
