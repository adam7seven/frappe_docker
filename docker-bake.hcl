# Docker Buildx Bake build definition file
# Reference: https://github.com/docker/buildx/blob/master/docs/reference/buildx_bake.md

variable "REGISTRY_USER" {
    default = "adam7"
}

variable PYTHON_VERSION {
    default = "3.11.6"
}
variable NODE_VERSION {
    default = "20.19.2"
}

variable "FRAPPE_VERSION" {
    default = "develop"
}

variable "FRAPPE_REPO" {
    default = "https://github.com/adam7seven/frappe"
}

variable "BENCH_REPO" {
    default = "https://github.com/frappe/bench"
}

variable "LATEST_BENCH_RELEASE" {
    default = "latest"
}

# Bench image

target "bench" {
    args = {
        GIT_REPO = "${BENCH_REPO}"
    }
    context = "images/bench"
    target = "bench"
    tags = [
        "frappe/bench:${LATEST_BENCH_RELEASE}",
        "frappe/bench:latest",
    ]
}

target "bench-test" {
    inherits = ["bench"]
    target = "bench-test"
}

# Main images
# Base for all other targets

group "default" {
    targets = ["frappe", "base", "build"]
}

function "tag" {
    params = [repo, version]
    result = [
      # Push frappe branch as tag
      "${REGISTRY_USER}/${repo}:${version}",
      # If `version` param is develop (development build) then use tag `latest`
      "${version}" == "develop" ? "${REGISTRY_USER}/${repo}:latest" : "${REGISTRY_USER}/${repo}:${version}",
      # Make short tag for major version if possible. For example, from v13.16.0 make v13.
      can(regex("(v[0-9]+)[.]", "${version}")) ? "${REGISTRY_USER}/${repo}:${regex("(v[0-9]+)[.]", "${version}")[0]}" : "",
      # Make short tag for major version if possible. For example, from v13.16.0 make version-13.
      can(regex("(v[0-9]+)[.]", "${version}")) ? "${REGISTRY_USER}/${repo}:version-${regex("([0-9]+)[.]", "${version}")[0]}" : "",
    ]
}

target "default-args" {
    args = {
        FRAPPE_PATH = "${FRAPPE_REPO}"
        BENCH_REPO = "${BENCH_REPO}"
        FRAPPE_BRANCH = "${FRAPPE_VERSION}"
        PYTHON_VERSION = "${PYTHON_VERSION}"
        NODE_VERSION = "${NODE_VERSION}"
    }
}

target "frappe" {
    inherits = ["default-args"]
    context = "."
    dockerfile = "images/production/Containerfile"
    target = "frappe"
    tags = tag("frappe", "${FRAPPE_VERSION}")
}

target "base" {
    inherits = ["default-args"]
    context = "."
    dockerfile = "images/production/Containerfile"
    target = "base"
    tags = tag("base", "${FRAPPE_VERSION}")
}

target "build" {
    inherits = ["default-args"]
    context = "."
    dockerfile = "images/production/Containerfile"
    target = "build"
    tags = tag("build", "${FRAPPE_VERSION}")
}
