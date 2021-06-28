import pytest

from pysisyphus.calculators.AnaPot import AnaPot
from pysisyphus.helpers import geom_loader
from pysisyphus.optimizers.LBFGS import LBFGS
from pysisyphus.testing import using
from pysisyphus.calculators.PySCF import PySCF


@pytest.mark.skip
@using("pyscf")
@pytest.mark.parametrize("line_search", [True, False])
def test_lbfgs_line_search(line_search):
    geom = geom_loader("lib:benzene_shaken.xyz")
    geom.set_calculator(PySCF(basis="sto3g", pal=6, verbose=0))

    opt_kwargs = {
        "line_search": line_search,
        "thresh": "gau_tight",
    }
    opt = LBFGS(geom, **opt_kwargs)
    opt.run()

    assert opt.is_converged


@pytest.mark.parametrize("line_search", [True, False])
def test_anapot_lbfgs_line_search(line_search):
    pot = AnaPot()
    geom = pot.get_geom((-0.7, 2.46, 0.0))
    opt_kwargs = {
        "line_search": line_search,
    }
    opt = LBFGS(geom, **opt_kwargs)
    opt.run()
    # pot.plot_opt(opt, show=True)

    assert opt.is_converged