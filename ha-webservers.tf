variable ssh_key {}

resource "cloudscale_server" "keepalived" {
  count               = 2
  name                = "keepalived0${count.index}"
  flavor_slug         = "flex-2"
  image_slug          = "debian-9"
  volume_size_gb      = 10
  ssh_keys            = ["${var.ssh_key}"]
}
