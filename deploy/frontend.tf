
resource "google_storage_bucket" "static_frontend" {
  name                        = "millennia-tech-tree-grapher-frontend"
  location                    = "US"
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  website {
    main_page_suffix = "upgrade-tree.html"
  }
}

# Make bucket public by granting allUsers storage.objectViewer access
resource "google_storage_bucket_iam_member" "public_rule" {
  bucket = google_storage_bucket.static_frontend.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

resource "google_storage_bucket_object" "frontend-html" {
  name         = "upgrade-tree.html"
  source       = "../frontend/upgrade-tree.html"
  bucket       = google_storage_bucket.static_frontend.id
  content_type = "text/html"
}

resource "google_storage_bucket_object" "frontend-controls" {
  name         = "controls.js"
  source       = "../frontend/controls.js"
  bucket       = google_storage_bucket.static_frontend.id
  content_type = "text/javascript"
}

resource "google_storage_bucket_object" "frontend-css" {
  name         = "styles.css"
  source       = "../frontend/styles.css"
  bucket       = google_storage_bucket.static_frontend.id
  content_type = "text/css"
}
