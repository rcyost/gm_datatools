from gm_datatools import gm_fred
import pandas as pd

def test_haversine() -> None:
    assert gm_fred.gm_test([0, 1, 2]) == pd.DataFrame({'col': [0, 1, 2]})

