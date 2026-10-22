"""Cross-platform archive paths and portable launcher boundaries."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('verify_handoff',ROOT/'scripts/verify_handoff.py')
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def test_historical_windows_paths():
    assert audit.relative_path(r'solution\result.toml')==Path('solution')/'result.toml'
    assert audit.relative_path('src/kerr_scalar_precision.jl')==Path('src')/'kerr_scalar_precision.jl'


@pytest.mark.parametrize('value',[r'C:\private\file',r'..\outside','/etc/passwd',r'C:relative'])
def test_archive_paths_stay_relative(value):
    with pytest.raises(ValueError):
        audit.relative_path(value)


def test_native_dry_run_preserves_files(tmp_path):
    command=[sys.executable,str(ROOT/'scripts/run_scalar_precision.py'),
             '--case','portable-smoke','--omega','0.1','--julia',sys.executable,
             '--output-root',str(tmp_path),'--dry-run']
    completed=subprocess.run(command,capture_output=True,text=True,check=True)
    record=json.loads(completed.stdout)
    assert record['precision']==[320,48,64,80,64]
    assert record['command'][-10:]==['0.5','0.1','0','0','1','320','48','64','80','64']
    assert not list(tmp_path.iterdir())
    (tmp_path/'portable-smoke').mkdir()
    assert subprocess.run(command,capture_output=True).returncode!=0
