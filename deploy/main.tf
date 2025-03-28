provider "google" {
  project     = var.project
  region      = "us-central1"
}

module "im-workspace" {
  source = "terraform-google-modules/bootstrap/google//modules/im_cloudbuild_workspace"
  version = "~> 11.0"
  tf_version = "1.5.7"

  project_id = var.project
  deployment_id = var.deployment_name
  im_deployment_repo_uri = var.git_repo
  im_deployment_ref = var.im_deployment_ref
  im_deployment_repo_dir = "deploy"
  infra_manager_sa = "projects/${var.project}/serviceAccounts/terraform-runner@millennia-tech-tree-grapher.iam.gserviceaccount.com"

  github_app_installation_id = var.github_app_installation_id
  github_pat_secret = var.github_pat_secret
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

    service_account = google_service_account.grapher.id
  }
}

resource "google_cloud_run_service_iam_member" "allow_unauthenticated" {
  service  = google_cloud_run_v2_service.default.name
  location = google_cloud_run_v2_service.default.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
