#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2019, Kovid Goyal <kovid at kovidgoyal.net>

import os
import sys

from virtual_machine.run import shutdown, wait_for_ssh

from .chroot import Chroot, process_args
from .constants import base_dir
from .vms import Rsync, get_vm_spec


def main(args=tuple(sys.argv)):
    arch, args = process_args(args)
    vm = get_vm_spec('linux', arch)
    chroot = Chroot(arch)
    if not chroot.single_instance():
        raise SystemExit('Another instance of the Linux container is running')
    if len(args) > 1:
        if args[1] == 'shutdown':
            shutdown(vm)
            return
        if args[1] == 'vm':
            chroot.build_vm()
            return

    chroot.ensure_vm_is_built(vm)

    port = wait_for_ssh(vm)
    rsync = Rsync(vm, port)
    output_dir = os.path.join(base_dir(), 'b', 'linux', arch, 'dist')
    pkg_dir = os.path.join(base_dir(), 'b', 'linux', arch, 'pkg')
    sources_dir = os.path.join(base_dir(), 'b', 'sources-cache')
    os.makedirs(sources_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(pkg_dir, exist_ok=True)

    cmd = ['python3', os.path.join('/', 'bypy'), 'main']
    rsync.main(sources_dir, pkg_dir, output_dir, cmd, list(args))


if __name__ == '__main__':
    main()
