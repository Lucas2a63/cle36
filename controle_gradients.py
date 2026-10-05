"""Contrôle : les gradients analytiques des deux réseaux égalent les différences finies (float64).
Ne lit pas les données. Usage : python3 controle_gradients.py"""
import numpy as np
import echelle as E

E.F32 = np.float64                     # précision double pour la vérification seulement


def perte(net, X, y, w):
    z = net.avant(X)[0]
    z = z - z.max(2, keepdims=True)
    lp = z - np.log(np.exp(z).sum(2, keepdims=True))
    return -(np.take_along_axis(lp, y[:, :, None], 2)[:, :, 0] * w).sum()


def gradient(net, X, y, w):
    z, _, cache = net.avant(X)
    z = z - z.max(2, keepdims=True)
    p = np.exp(z); p /= p.sum(2, keepdims=True)
    np.put_along_axis(p, y[:, :, None], np.take_along_axis(p, y[:, :, None], 2) - 1, 2)
    return net.arriere(p * w[:, :, None], cache)


def controler(arch):
    rng = np.random.default_rng(0)
    net = {"mlp": E.MLP, "cnn": E.CNN}[arch](rng)
    for k in net.POIDS:                                  # tout en double, biais non nuls
        setattr(net, k, getattr(net, k).astype(np.float64) + 0.05 * rng.normal(size=getattr(net, k).shape))
    X = rng.normal(size=(E.M, 3, 16, 16, 3))
    y = rng.integers(0, 10, (E.M, 3))
    w = rng.uniform(0.5, 2, (E.M, 3))
    gr = gradient(net, X, y, w)
    pire = 0.0
    for k in net.POIDS:
        W = getattr(net, k)
        for _ in range(6):
            i = tuple(rng.integers(0, s) for s in W.shape)
            h = 1e-6
            W[i] += h; lp = perte(net, X, y, w)
            W[i] -= 2 * h; lm = perte(net, X, y, w)
            W[i] += h
            num = (lp - lm) / (2 * h)
            err = abs(num - gr[k][i]) / max(1e-8, abs(num) + abs(gr[k][i]))
            pire = max(pire, err)
    print(f"{arch} : écart relatif maximal {pire:.2e}  ({'bon' if pire < 1e-5 else 'FAUX'})")
    return pire < 1e-5


if __name__ == "__main__":
    ok = controler("mlp") & controler("cnn")
    raise SystemExit(0 if ok else 1)
