"""Portable bounded launcher for the preserved scalar BigFloat solver."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = {'coarse': (320, 48, 64, 80, 64), 'fine': (384, 64, 80, 112, 88)}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', required=True, help='Fresh output directory name')
    parser.add_argument('--omega', required=True)
    parser.add_argument('--spin', default='0.5')
    parser.add_argument('--ell', type=int, default=0)
    parser.add_argument('--m', type=int, default=0)
    parser.add_argument('--n', type=int, default=1)
    parser.add_argument('--resolution', choices=SETTINGS, default='coarse')
    for flag in ('bits', 'outer-order', 'inner-order', 'quad', 'levin'):
        parser.add_argument('--'+flag, type=int)
    parser.add_argument('--julia', default=os.environ.get('JULIA', 'julia'))
    parser.add_argument('--wsl-distro', help='Optional Windows-to-WSL execution')
    parser.add_argument('--timeout', type=int, default=300)
    parser.add_argument('--output-root', type=Path, default=ROOT/'results/precision_runs')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', args.case):
        parser.error('--case must be a single simple directory name')
    if args.ell < abs(args.m) or args.n < 1 or args.timeout < 1:
        parser.error('require ell >= abs(m), n >= 1, timeout > 0')
    overrides = (args.bits, args.outer_order, args.inner_order, args.quad, args.levin)
    settings = tuple(default if value is None else value
                     for default, value in zip(SETTINGS[args.resolution], overrides))
    if any(value < 2 for value in settings):
        parser.error('precision and orders must be at least 2')
    folder = args.output_root.resolve()/args.case
    if folder.exists():
        parser.error(f'preserving existing output: {folder}')
    driver = ROOT/'scripts/run_scalar_precision_20261023.jl'
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', JULIA_NUM_THREADS='1')
    if args.wsl_distro:
        if os.name != 'nt':
            parser.error('--wsl-distro is a Windows launcher option; use native Julia here')
        wsl = ['wsl.exe', '-d', args.wsl_distro, '-e']
        def target(path):
            return subprocess.check_output(wsl+['wslpath', '-a', str(path)],
                                           encoding='utf8').strip()
        prefix = wsl+['env', 'OPENBLAS_NUM_THREADS=1', 'JULIA_NUM_THREADS=1']
        command = prefix+['timeout', '--kill-after=10', str(args.timeout), args.julia]
        version_command = prefix+[args.julia, '--version']
        driver_target, output_target = target(driver), target(folder/'solution')
    else:
        runtime = shutil.which(args.julia)
        if runtime is None:
            parser.error('Julia not found; set --julia or the JULIA environment variable')
        command, version_command = [runtime], [runtime, '--version']
        driver_target, output_target = str(driver), str(folder/'solution')
    command += ['--startup-file=no', '--threads=1', driver_target, output_target,
                args.spin, args.omega, str(args.ell), str(args.m), str(args.n),
                *map(str, settings)]
    if args.dry_run:
        print(json.dumps({'command': command, 'output': str(folder), 'precision': settings}, indent=2))
        return
    version = subprocess.check_output(version_command, env=env, encoding='utf8', timeout=15).strip()
    folder.mkdir(parents=True)
    sources = [ROOT/'src/kerr_scalar_precision.jl', driver, Path(__file__)]
    before = {p.relative_to(ROOT).as_posix(): sha(p) for p in sources}
    snapshot = folder/'source_snapshot'
    snapshot.mkdir()
    for p in sources:
        shutil.copyfile(p, snapshot/p.name)
    started = time.monotonic()
    status, returncode = 'failed', None
    try:
        with (folder/'stdout.txt').open('w', encoding='utf8') as out, (folder/'stderr.txt').open('w', encoding='utf8') as err:
            result = subprocess.run(command, env=env, stdout=out, stderr=err,
                                    timeout=args.timeout+(20 if args.wsl_distro else 0))
            returncode = result.returncode
            status = 'completed' if returncode == 0 else ('timeout' if returncode == 124 else 'failed')
    except subprocess.TimeoutExpired:
        status = 'timeout'
    finally:
        after = {p.relative_to(ROOT).as_posix(): sha(p) for p in sources}
        if before != after:
            status = 'inputs-changed'
        outputs = {p.relative_to(folder).as_posix(): sha(p)
                   for p in folder.rglob('*') if p.is_file()}
        record = dict(status=status, returncode=returncode, command=command,
                      seconds=time.monotonic()-started, precision=settings,
                      source_hashes_before=before, source_hashes_after=after, outputs=outputs,
                      python=sys.version, platform=platform.platform(), julia=version,
                      timeout_seconds=args.timeout, memory_guard_bytes=1500000000,
                      memory_guard_scope='Julia guard; current RSS on Linux, peak RSS on other systems',
                      parameters=dict(a=args.spin,omega=args.omega,ell=args.ell,m=args.m,n=args.n),
                      assertion_tested='Scalar homogeneous residual and first-order nonlinear response; single run pending refinement')
        (folder/'manifest.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':status,'output':str(folder),'seconds':record['seconds']},indent=2))
    if status != 'completed':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
