# Slot-B vendor capacity finding

The read-only Slot-B lpdump shows vendor_b as one extent containing
1,594,432 512-byte sectors.

Therefore:

- vendor_b allocation: 816,349,184 bytes
- verified fixed vendor.img: 816,353,280 bytes
- shortfall: 4,096 bytes
- shortfall: 8 sectors

The fixed vendor filesystem/original AVB image also grew by exactly one
4 KiB block:

- old: 800,976,896 bytes
- fixed: 800,980,992 bytes

DIRECT_FLASH_FIT=0

No flash, resize, slot change, or phone reboot occurred during this
derivation.

AVB maximum original-image size with the current partition allocation:

Traceback (most recent call last):
  File "/home/armol/.local/bin/avbtool", line 5052, in <module>
    tool.run(sys.argv)
    ~~~~~~~~^^^^^^^^^^
  File "/home/armol/.local/bin/avbtool", line 4834, in run
    args.func(args)
    ~~~~~~~~~^^^^^^
  File "/home/armol/.local/bin/avbtool", line 4930, in add_hashtree_footer
    self.avb.add_hashtree_footer(
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        args.image.name if args.image else None,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<25 lines>...
        args.no_hashtree,
        ^^^^^^^^^^^^^^^^^
        args.check_at_most_once)
        ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/armol/.local/bin/avbtool", line 3703, in add_hashtree_footer
    max_fec_size = calc_fec_data_size(partition_size, fec_num_roots)
  File "/home/armol/.local/bin/avbtool", line 4105, in calc_fec_data_size
    p = subprocess.Popen(
        ['fec', '--print-fec-size', str(image_size), '--roots', str(num_roots)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
  File "/usr/lib/python3.14/subprocess.py", line 1039, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                        pass_fds, cwd, env,
                        ^^^^^^^^^^^^^^^^^^^
    ...<5 lines>...
                        gid, gids, uid, umask,
                        ^^^^^^^^^^^^^^^^^^^^^^
                        start_new_session, process_group)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/subprocess.py", line 1990, in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'fec'

AVB maximum original-image size with a +4096-byte allocation:

Traceback (most recent call last):
  File "/home/armol/.local/bin/avbtool", line 5052, in <module>
    tool.run(sys.argv)
    ~~~~~~~~^^^^^^^^^^
  File "/home/armol/.local/bin/avbtool", line 4834, in run
    args.func(args)
    ~~~~~~~~~^^^^^^
  File "/home/armol/.local/bin/avbtool", line 4930, in add_hashtree_footer
    self.avb.add_hashtree_footer(
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        args.image.name if args.image else None,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<25 lines>...
        args.no_hashtree,
        ^^^^^^^^^^^^^^^^^
        args.check_at_most_once)
        ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/armol/.local/bin/avbtool", line 3703, in add_hashtree_footer
    max_fec_size = calc_fec_data_size(partition_size, fec_num_roots)
  File "/home/armol/.local/bin/avbtool", line 4105, in calc_fec_data_size
    p = subprocess.Popen(
        ['fec', '--print-fec-size', str(image_size), '--roots', str(num_roots)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
  File "/usr/lib/python3.14/subprocess.py", line 1039, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                        pass_fds, cwd, env,
                        ^^^^^^^^^^^^^^^^^^^
    ...<5 lines>...
                        gid, gids, uid, umask,
                        ^^^^^^^^^^^^^^^^^^^^^^
                        start_new_session, process_group)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/subprocess.py", line 1990, in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'fec'
