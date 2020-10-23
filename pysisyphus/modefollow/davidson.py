# [1] https://aip.scitation.org/doi/pdf/10.1063/1.1523908
#     Neugebauer, Reiher 2002
# [2] https://reiher.ethz.ch/software/akira.html


from collections import namedtuple

import numpy as np

from pysisyphus.helpers_pure import eigval_to_wavenumber
from pysisyphus.Geometry import get_trans_rot_projector
from pysisyphus.modefollow.NormalMode import NormalMode


def fin_diff(geom, b, step_size):
    m_sqrt = np.sqrt(geom.masses_rep)
    plus = geom.get_energy_and_forces_at(geom.coords + b)["forces"]
    minus = geom.get_energy_and_forces_at(geom.coords - b)["forces"]
    fd = (minus - plus) / (2 * step_size) / m_sqrt
    return fd


DavidsonResult = namedtuple(
    "DavidsonResult",
    "cur_cycle nus mode_ind",
)

BlockDavidsonResult = namedtuple(
    "BlockDavidsonResult",
    "cur_cycle nus mode_inds",
)


def davidson(
    geom,
    mode_guess,
    trial_step_size=0.01,
    hessian_precon=None,
    max_cycles=25,
    res_rms_thresh=1e-4,
):
    if hessian_precon is not None:
        print("Using supplied Hessians as preconditioner.")

    B_full = np.zeros((len(mode_guess), max_cycles))
    S_full = np.zeros_like(B_full)
    msqrt = np.sqrt(geom.masses_rep)

    # Projector to remove translation and rotation
    P = get_trans_rot_projector(geom.cart_coords, geom.masses)
    l_proj = P.dot(mode_guess.l_mw) / msqrt
    mode_guess = NormalMode(l_proj, geom.masses_rep)

    b_prev = mode_guess.l_mw
    for i in range(max_cycles):
        print(f"Cycle {i:02d}")
        b = mode_guess.l_mw
        B_full[:, i] = b

        # Overlaps of basis vectors in B
        # B_ovlp = np.einsum("ij,kj->ik", B, B)

        # Estimate action of Hessian on basis vector by finite differences
        #
        # Get step size in mass-weighted coordinates that results
        # in the desired 'trial_step_size' in not-mass-weighted coordinates.
        mw_step_size = mode_guess.mw_norm_for_norm(trial_step_size)
        # Actual step in non-mass-weighted coordinates
        step = trial_step_size * mode_guess.l
        S_full[:, i] = fin_diff(geom, step, mw_step_size)

        # Views on columns that are actually set
        B = B_full[:, : i + 1]
        S = S_full[:, : i + 1]

        # Calculate and symmetrize approximate hessian
        Hm = B.T.dot(S)
        Hm = (Hm + Hm.T) / 2
        # Diagonalize small Hessian
        w, v = np.linalg.eigh(Hm)

        # i-th approximation to exact eigenvector
        approx_modes = (v * B[:, :, None]).sum(axis=1).T

        # Calculate overlaps between previous root and the new approximate
        # normal modes for root following.
        mode_overlaps = (approx_modes * b_prev).sum(axis=1)
        mode_ind = np.abs(mode_overlaps).argmax()
        print(f"\tFollowing mode {mode_ind}")

        residues = list()
        for s in range(i + 1):
            residues.append((v[:, s] * (S - w[s] * B)).sum(axis=1))
        residues = np.array(residues)

        b_prev = approx_modes[mode_ind]

        # Construct new basis vector from residuum of selected mode
        if hessian_precon is not None:
            # Construct X
            X = np.linalg.inv(
                hessian_precon - w[mode_ind] * np.eye(hessian_precon.shape[0])
            )
            b = X.dot(residues[mode_ind])
        else:
            b = residues[mode_ind]
        # Project out translation and rotation from new mode guess
        b = P.dot(b)
        # Orthogonalize new mode against current basis vectors
        rows, cols = B.shape
        B_ = np.zeros((rows, cols + 1))
        B_[:, :cols] = B
        B_[:, -1] = b
        b, _ = np.linalg.qr(B_)

        # New NormalMode from non-mass-weighted displacements
        mode_guess = NormalMode(b[:, -1] / msqrt, geom.masses_rep)

        # Calculate wavenumbers
        nus = eigval_to_wavenumber(w)

        # Check convergence criteria
        max_res = np.abs(residues).max(axis=1)
        res_rms = np.sqrt(np.mean(residues ** 2, axis=1))

        # Print progress
        print("\t #  |      wavelength       |  rms       |   max")
        for j, (nu, rms, mr) in enumerate(zip(nus, res_rms, max_res)):
            sel_str = "*" if (j == mode_ind) else " "
            print(f"\t{j:02d}{sel_str} | {nu:> 16.2f} cm⁻¹ | {rms:.8f} | {mr:.8f}")
        print()

        if res_rms[mode_ind] < res_rms_thresh:
            print("Converged!")
            break

    result = DavidsonResult(
        cur_cycle=i,
        nus=nus,
        mode_ind=mode_ind,
    )

    return result


def block_davidson(
    geom,
    guess_modes,
    trial_step_size=0.01,
    hessian_precon=None,
    max_cycles=25,
    res_rms_thresh=1e-4,
):
    num = len(guess_modes)
    B_full = np.zeros((len(guess_modes[0]), num * max_cycles))
    S_full = np.zeros_like(B_full)
    msqrt = np.sqrt(geom.masses_rep)

    # Projector to remove translation and rotation
    P = get_trans_rot_projector(geom.cart_coords, geom.masses)
    guess_modes = [
        NormalMode(P.dot(mode.l_mw) / msqrt, geom.masses_rep) for mode in guess_modes
    ]

    b_prev = np.array([mode.l_mw for mode in guess_modes]).T
    for i in range(max_cycles):
        print(f"Cycle {i:02d}")
        # Add new basis vectors to B matrix
        b = np.array([mode.l_mw for mode in guess_modes]).T
        from_ = i * num
        to_ = (i + 1) * num
        B_full[:, from_:to_] = b
        # Orthogonalize new mode against current basis vectors
        B_full, _ = np.linalg.qr(B_full)

        # Overlaps of basis vectors in B
        # B_ovlp = np.einsum("ij,kj->ik", B, B)

        # Estimate action of Hessian by finite differences.
        for j in range(num):
            mode = guess_modes[j]
            # Get a step size in mass-weighted coordinates that results
            # in the desired 'trial_step_size' in not-mass-weighted coordinates.
            mw_step_size = mode.mw_norm_for_norm(trial_step_size)
            # Actual step in non-mass-weighted coordinates
            step = trial_step_size * mode.l
            S_full[:, from_+j] = fin_diff(geom, step, mw_step_size)

        # Views on columns that are actually set
        B = B_full[:, : to_]
        S = S_full[:, : to_]

        # Calculate and symmetrize approximate hessian
        Hm = B.T.dot(S)
        Hm = (Hm + Hm.T) / 2
        # Diagonalize small Hessian
        w, v = np.linalg.eigh(Hm)

        # Approximations to exact eigenvectors in current cycle
        approx_modes = (v * B[:, :, None]).sum(axis=1).T
        # Calculate overlaps between previous root and the new approximate
        # normal modes for root following.
        overlaps = np.einsum("ij,ji->i", approx_modes, b_prev)
        mode_inds = np.abs(overlaps).argsort()[-num:]
        print(f"\tFollowing mode(s): {mode_inds}")
        b_prev = approx_modes[mode_inds].T

        residues = list()
        for s in range(to_):
            residues.append((v[:, s] * (S - w[s] * B)).sum(axis=1))
        residues = np.array(residues)

        # Construct new basis vector from residuum of selected mode
        if hessian_precon is not None:
            # Construct X
            b = np.zeros_like(b_prev)
            for j, mode_ind in enumerate(mode_inds):
                X = np.linalg.inv(
                    hessian_precon - w[mode_ind] * np.eye(hessian_precon.shape[0])
                )
                b[:,j] = X.dot(residues[mode_ind].T)
        else:
            b = residues[mode_inds].T
        # Project out translation and rotation from new mode guess
        b = P.dot(b)
        b = np.linalg.qr(np.concatenate((B, b), axis=1))[0][:,-num][:, None]

        # import pdb; pdb.set_trace()
        # mode_guess = NormalMode(b[:, -1] / msqrt, geom.masses_rep)
        # New NormalMode from non-mass-weighted displacements
        guess_modes = [
            NormalMode(b_ / msqrt, geom.masses_rep)
            for b_ in b.T
        ]

        # Calculate wavenumbers
        nus = eigval_to_wavenumber(w)

        # Check convergence criteria
        max_res = np.abs(residues).max(axis=1)
        res_rms = np.sqrt(np.mean(residues ** 2, axis=1))

        # Print progress
        print("\t #  |      wavelength       |  rms       |   max")
        for j, (nu, rms, mr) in enumerate(zip(nus, res_rms, max_res)):
            sel_str = "*" if (j in mode_inds) else " "
            print(f"\t{j:02d}{sel_str} | {nu:> 16.2f} cm⁻¹ | {rms:.8f} | {mr:.8f}")
        print()

        if all(res_rms[mode_inds] < res_rms_thresh):
            print("Converged!")
            break

    result = BlockDavidsonResult(
        cur_cycle=i,
        nus=nus,
        mode_inds=mode_inds,
    )

    return result
