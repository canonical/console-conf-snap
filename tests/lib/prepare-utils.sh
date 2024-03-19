#!/bin/bash

set -e
set -x

get_arch() {
    if os.query is-pc-amd64; then
        printf amd64
    elif os.query is-arm64; then
        printf arm64
    else
        printf "ERROR: unsupported archtecture\n"
        exit 1
    fi
}

get_snap_name() {
    # SNAP_NAME is set in spread.yaml
    echo "${SNAP_NAME}.snap"
}

install_base_deps() {
    sudo apt update -qq

    # these should already be installed in GCE and LXD images with the google/lxd-nested 
    # backend, but in qemu local images from qemu-nested, we might not have them
    sudo apt install psmisc fdisk snapd mtools ovmf qemu-system-x86 sshpass whois -yqq

    sudo snap install ubuntu-image --classic --channel=latest/edge
}

download_core24_snaps() {
    # get the model
    curl -o ubuntu-core-dangerous.model \
         "https://raw.githubusercontent.com/snapcore/models/master/ubuntu-core-24-$(get_arch)-dangerous.model"

    # download essential snaps
    snap download pc-kernel --channel=24/${KERNEL_CHANNEL} --basename=upstream-pc-kernel
    snap download pc --channel=24/${GADGET_CHANNEL} --basename=upstream-pc-gadget
    snap download snapd --channel=${SNAPD_CHANNEL} --basename=upstream-snapd
    snap download core24 --channel=${BASE_CHANNEL} --basename=upstream-core24
}

build_snap() {
    local project_dir="$1"
    local current_dir="$(pwd)"
    
    # run snapcraft
    (
        cd "$project_dir"
        snapcraft --verbosity verbose --output "$(get_snap_name)"

        # copy the snap to the calling directory if they are not the same
        if [ "$project_dir" != "$current_dir" ]; then
            cp "$(get_snap_name)" "$current_dir"
        fi
    )
}

build_base_image() {
    local snap_name="$(get_snap_name)"
    ubuntu-image snap \
        -i 8G \
        --snap upstream-snapd.snap \
        --snap upstream-pc-kernel.snap \
        --snap upstream-pc-gadget.snap \
        --snap upstream-core24.snap \
        --snap $snap_name \
        ubuntu-core-dangerous.model
}
