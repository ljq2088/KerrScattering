"""Bounded, single-process scalar precision experiments with immutable runs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import tomllib

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = '/tmp/codex-julia-20261023/julia-1.10.7/bin/julia'
DISTRO = 'Ubuntu-22.04-D'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--suite', choices=['low', 'high', 'control'], required=True)
    parser.add_argument('--resolution', choices=['coarse', 'fine'], required=True)
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    suites = {
        'low': [(l, 0, w, 1) for l in (0, 1, 2) for w in ('0.00001', '0.0001')]
               + [(0, 0, '0.00001', n) for n in (2, 3)],
        'high': [(0, 0, w, 1) for w in ('1', '2', '3', '5', '10')]
                + [(l, 0, '3', 1) for l in (1, 2)]
                + [(0, 0, '3', n) for n in (2, 3)],
        'control': [(0, 0, '0.1', 1), (2, 2, '1', 1)],
    }
    cases = suites[args.suite][:args.limit]
    settings = {'coarse': (320, 48, 64, 80, 64),
                'fine': (384, 64, 80, 112, 88)}[args.resolution]
    base = subprocess.check_output(['wsl.exe', '-d', DISTRO, '-e', 'wslpath', '-a', str(ROOT)], text=True, encoding='utf8').strip()
    sources = [ROOT/'src/kerr_scalar_precision.jl', ROOT/'scripts/run_scalar_precision_20261023.jl', Path(__file__)]
    for l, m, omega, n in cases:
        name = f'{args.suite}_l{l}_m{m}_w{omega}_n{n}_{args.resolution}'
        folder = ROOT/'results/precision_20261023'/name
        if folder.exists():
            print(f'Preserving existing run {name}', flush=True)
            continue
        folder.mkdir(parents=True)
        before = {str(p.relative_to(ROOT)): digest(p) for p in sources}
        parameters = ['0.5', omega, str(l), str(m), str(n), *map(str, settings)]
        command = ['wsl.exe', '-d', DISTRO, '-e', 'env', 'OPENBLAS_NUM_THREADS=1',
                   'JULIA_NUM_THREADS=1', 'timeout', '--kill-after=10', '300', RUNTIME,
                   '--startup-file=no', '--threads=1', base+'/scripts/run_scalar_precision_20261023.jl',
                   base+'/results/precision_20261023/'+name+'/solution', *parameters]
        print('RUN', name, flush=True)
        started = time.time()
        with (folder/'stdout.txt').open('w', encoding='utf8') as out, (folder/'stderr.txt').open('w', encoding='utf8') as err:
            completed = subprocess.run(command, stdout=out, stderr=err, timeout=330)
        after = {str(p.relative_to(ROOT)): digest(p) for p in sources}
        status = 'completed' if completed.returncode == 0 else 'failed'
        if before != after:
            status = 'inputs-changed'
        outputs = {str(p.relative_to(folder)): digest(p) for p in folder.rglob('*') if p.is_file()}
        record = dict(status=status, returncode=completed.returncode, command=command,
                      seconds=time.time()-started, source_hashes_before=before, source_hashes_after=after,
                      outputs=outputs, python=sys.version, runtime='Julia 1.10.7 official Linux x86_64',
                      runtime_archive_sha256='21b2c69806aacf191d7c81806c7d9918bddab30c7b5b8d4251389c3abe274334',
                      assertion_tested=f'M=1,a=0.5,s=0,l={l},m={m},omega={omega},n={n}; homogeneous residuals, complex nonlinear response, flux-phase bound',
                      precision=settings, timeout_seconds=300, memory_guard_bytes=1500000000,
                      non_claims=['R1 uses the exact self-channel decomposition; its balance is algebraic.',
                                  'One resolution is provisional until independently refined.'])
        (folder/'manifest.json').write_text(json.dumps(record, indent=2), encoding='utf8')
        print(status, record['seconds'], flush=True)
        print((folder/'stdout.txt').read_text(encoding='utf8')[-1000:], flush=True)
        if status != 'completed':
            print((folder/'stderr.txt').read_text(encoding='utf8')[-1800:], flush=True)
            raise SystemExit(1)


if __name__ == '__main__':
    main()
