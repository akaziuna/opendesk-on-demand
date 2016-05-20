# -*- coding: utf-8 -*-

"""Provides the main command line and plugin entry points."""

from __future__ import print_function

import argparse
import json
import subprocess
import os
import os.path

from . import generate

def is_within_git_repo():
    with open(os.devnull, 'w') as out:
        cmd = ["git", "branch"]
        exit_code = subprocess.call(cmd, stderr=out, stdout=out)
    return exit_code is 0

def default_output_dir():
    if is_within_git_repo():
        here = os.path.dirname(__file__)
        return os.path.join(here, '..', '..', '.build')
    return os.path.expanduser('~/.opendesk-on-demand')

def get_output_dir():
    key = 'OPENDESK_ON_DEMAND_OUTPUT_DIR'
    default = default_output_dir()
    return os.environ.get(key, default)

def write_to_filesystem(name, target_dir, model_units, extension, output_dir=None):
    """Python entry point to write the generated files to an output folder."""

    # Parse the target_dir to generate the data.
    generator = generate.Generator(target_dir, model_units, extension=extension)
    obj_data, config_data = generator()

    # Make sure the output folder exists.
    if output_dir is None:
        output_dir = get_output_dir()
    model_dir = os.path.join(output_dir, name)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    # Write the `obj.json`.
    obj_json = json.dumps(obj_data, indent=2)
    obj_filepath = os.path.join(model_dir, 'obj.json')
    with open(obj_filepath, 'w') as f:
        f.write(obj_json)

    # Write the `config.json`.
    config_json = json.dumps(config_data, indent=2)
    config_filepath = os.path.join(model_dir, 'config.json')
    with open(config_filepath, 'w') as f:
        f.write(config_json)

    return model_dir

def post_to_webserver(name, target_dir, model_units, extension, **kwargs):
    """XXX"""

    # Parse the target_dir to generate the data.
    generator = generate.Generator(target_dir, model_units, extension=extension)
    obj_data, config_data = generator()

    # XXX Post to an API endpoint.
    raise NotImplementedError

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('target_dir')
    parser.add_argument('--extension', default=None)
    parser.add_argument('--mode', default=u'local', choices=['local', 'web'])
    parser.add_argument('--name', default=None)
    parser.add_argument('--output', default=None)
    parser.add_argument('--units', default='cm')
    return parser.parse_args()

def main():
    """Command line entry point."""

    args = parse_args()
    if args.mode == u'local':
        exporter = write_to_filesystem
        kwargs = {
            'output_dir': args.output,
        }
    else:
        exporter = post_to_webserver
        kwargs = {}
    target_dir = args.target_dir
    name = args.name if args.name else os.path.basename(target_dir)
    print('Compiling {0}'.format(name))
    output = exporter(name, target_dir, args.units, args.extension, **kwargs)
    print('Output:')
    print('- filesystem:')
    print(output)
    print('- localhost:')
    print('http://localhost:8000/demo.html?example={0}'.format(name))

if __name__ == '__main__':
    main()
