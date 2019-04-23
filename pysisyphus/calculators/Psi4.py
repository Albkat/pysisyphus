#!/usr/bin/env python3

import textwrap
import re

import numpy as np

from pysisyphus.calculators.Calculator import Calculator


class Psi4(Calculator):

    conf_key = "psi4"

    def __init__(self, method, basis, mem=2000, **kwargs):
        super().__init__(**kwargs)

        self.method = method
        self.basis = basis
        self.mem = mem

        self.inp_fn = "psi4.inp"
        self.out_fn = "psi4.out"

        self.parser_funcs = {
            "energy": self.parse_energy,
            "grad": self.parse_grad,
        }

        self.base_cmd = self.get_cmd("cmd")

        self.inp = """
        molecule mol{{
          {xyz}
        symmetry c1
        }}


        set basis {basis}
        {method}
        """

    def prepare_input(self, atoms, coords, calc_type):
        xyz = self.prepare_coords(atoms, coords)

        calc_types = {
            "grad": "G, wfn = gradient('{}', return_wfn=True)\n" \
                    "G_arr = np.array(G)\n" \
                    "np.save('grad', G_arr)",
            "energy": "energy('{}')",
        }
        method = calc_types[calc_type].format(self.method)

        inp = self.inp.format(
                xyz=xyz,
                basis=self.basis,
                method=method,
        )
        inp = "\n".join([line.strip() for line in inp.split("\n")])
        return inp

    def get_energy(self, atoms, coords):
        calc_type = "energy"
        inp = self.prepare_input(atoms, coords, calc_type)
        results = self.run(inp, calc="energy")
        return results

    def get_forces(self, atoms, coords):
        calc_type = "grad"
        inp = self.prepare_input(atoms, coords, calc_type)
        results = self.run(inp, calc="grad")
        return results

    def get_hessian(self, atoms, coords):
        calc_type = "freq"
        inp = self.prepare_input(atoms, coords, calc_type)
        results = self.run(inp, calc="hessian")
        return results

    def parse_energy(self, path):
        with open(path / "psi4.out") as handle:
            text = handle.read()
        en_regex = re.compile("Total Energy =\s*([\d\-\.]+)")
        mobj = en_regex.search(text)
        result = {
            "energy": float(mobj[1])
        }
        return result


    def parse_grad(self, path):
        gradient = np.load(path / "grad.npy")
        forces = -gradient.flatten()
        result = {
            "forces": forces,
        }
        result.update(self.parse_energy(path))
        return result

    def parse_hessian(self, path):
        pass
        # return results

    def keep(self, path):
        kept_fns = super().keep(path)

    def __str__(self):
        return f"Psi4({self.name})"


if __name__ == "__main__":
    psi4 = Psi4()
    print(psi4.cmd)
