"""Comment les fichiers de donnees/ ont été faits, à partir de l'archive originale de CIFAR-10
(Krizhevsky, 2009, https://www.cs.toronto.edu/~kriz/cifar.html, cifar-10-python.tar.gz,
MD5 c58f30108f718f92721af3b95e74349a). Chaque image 32×32 est réduite en 16×16 par moyenne des
blocs 2×2, arrondie à l'entier. Les sessions n'ont pas à le relancer : les fichiers sont dans le dépôt.

Usage : python3 preparer_donnees.py chemin/vers/cifar-10-python.tar.gz
"""
import hashlib, os, pickle, sys, tarfile
import numpy as np

MD5 = "c58f30108f718f92721af3b95e74349a"


def lire(tf, nom):
    d = pickle.load(tf.extractfile(f"cifar-10-batches-py/{nom}"), encoding="bytes")
    x = np.asarray(d[b"data"], np.uint8).reshape(-1, 3, 32, 32).transpose(0, 2, 3, 1)
    x16 = np.round(x.reshape(-1, 16, 2, 16, 2, 3).astype(np.float64).mean((2, 4))).astype(np.uint8)
    return x16, np.asarray(d[b"labels"], np.uint8)


if __name__ == "__main__":
    chemin = sys.argv[1]
    h = hashlib.md5(open(chemin, "rb").read()).hexdigest()
    assert h == MD5, f"archive inattendue (MD5 {h})"
    with tarfile.open(chemin, "r:gz") as tf:
        parts = [lire(tf, f"data_batch_{i}") for i in range(1, 6)]
        xt, yt = lire(tf, "test_batch")
    x = np.concatenate([p[0] for p in parts]); y = np.concatenate([p[1] for p in parts])
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "donnees")
    os.makedirs(d, exist_ok=True)
    np.savez_compressed(os.path.join(d, "cifar16_a.npz"), x=x[:25000], y=y[:25000])
    np.savez_compressed(os.path.join(d, "cifar16_b.npz"), x=x[25000:], y=y[25000:])
    np.savez_compressed(os.path.join(d, "cifar16_t.npz"), x=xt, y=yt)
    print("entraînement", x.shape, "test", xt.shape, "effectifs", np.bincount(y), np.bincount(yt))
