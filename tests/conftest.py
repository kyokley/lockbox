import pytest
import shutil


@pytest.fixture
def temp_dir(tmp_path):
    yield tmp_path
    if tmp_path.exists():
        shutil.rmtree(tmp_path)
