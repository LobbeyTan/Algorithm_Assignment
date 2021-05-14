import multiprocessing
import numpy as np
from scipy.io import wavfile
from python_speech_features import mfcc
from os import listdir
from pydub import AudioSegment
from pydub.silence import split_on_silence


def __getMin(cost, indexes, getVal=False):
    costs = [cost[i, j] if i >= 0 and j >= 0 else np.nan for i, j in indexes]

    if all(np.isnan(costs)):
        return 0 if getVal else (-1, -1)

    idx = np.nanargmin(costs)

    if getVal:
        return costs[idx]

    return indexes[idx]


def __distance(a, b):
    if a.ndim == b.ndim == 0:
        return abs(a - b)
    return np.linalg.norm(np.atleast_1d(a) - np.atleast_1d(b), 1)


def __reduceByHalf(x):
    return [(x[i] + x[1 + i]) / 2 for i in range(0, len(x) - len(x) % 2, 2)]


def __expandResWindow(lowResPath, X, Y, radius):
    path_ = set(lowResPath)
    for i, j in lowResPath:
        for a, b in ((i + a, j + b)
                     for a in range(-radius, radius + 1)
                     for b in range(-radius, radius + 1)):
            path_.add((a, b))

    window_ = set()
    for i, j in path_:
        for a, b in ((i * 2, j * 2), (i * 2, j * 2 + 1),
                     (i * 2 + 1, j * 2), (i * 2 + 1, j * 2 + 1)):
            window_.add((a, b))

    window = []
    start_j = 0
    for i in range(0, len(X)):
        new_start_j = None
        for j in range(start_j, len(Y)):
            if (i, j) in window_:
                window.append((i, j))
                if new_start_j is None:
                    new_start_j = j
            elif new_start_j is not None:
                break
        start_j = new_start_j

    return window


def dtw(series_1, series_2, window=None):
    m = len(series_1)
    n = len(series_2)

    if window is None:
        window = [(i, j) for i in range(m) for j in range(n)]

    cost = np.full(shape=(m, n), fill_value=np.nan)

    for i, j in window:
        adj_min = __getMin(cost, [(i - 1, j), (i, j - 1), (i - 1, j - 1)], getVal=True)
        cost[i, j] = __distance(series_1[i], series_2[j]) + adj_min

    (i, j) = (m - 1, n - 1)
    path = []
    distance = 0

    while i >= 0 or j >= 0:
        path += [(i, j)]
        distance += cost[i, j]
        (i, j) = __getMin(cost, [(i - 1, j), (i, j - 1), (i - 1, j - 1)])

    distance /= len(path)

    path.reverse()
    return distance, path


def fastDTW(X, Y, radius=1):
    minSize = radius + 2
    m = len(X)
    n = len(Y)

    if m < minSize or n < minSize:
        return dtw(X, Y)

    shrunkX = __reduceByHalf(X)
    shrunkY = __reduceByHalf(Y)

    distance, lowResPath = fastDTW(shrunkX, shrunkY, radius)

    window = __expandResWindow(lowResPath, X, Y, radius)

    return dtw(X, Y, window)


def split(path, filename, min_silence_len=100, silence_thresh=-50):
    samples = AudioSegment.from_wav(f"{path}{filename}")

    audio_chunks = split_on_silence(samples, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    print(len(audio_chunks))

    for i, chunk in enumerate(audio_chunks):
        out_file = f"split/{filename}{i}.wav"
        print("exporting", out_file)
        chunk.export(out_file, format="wav")


def getSources(directory):
    path = f"{directory}/"
    sources = []
    for fname in listdir(path):
        fs, data = wavfile.read(f"{path}{fname}")
        sources.append(mfcc(data, fs, nfft=1200))
    return sources


def runDTW(testWord: str, rtn: multiprocessing.Array, sourceDirectory="split", limit=95):
    sources = getSources(sourceDirectory)
    try:
        fs, test = wavfile.read(f"test/{testWord}")
        # print(test.shape)
    except FileNotFoundError:
        print(f"File not found: no audio file named {testWord}")
        return False, -1, None
    test = mfcc(test, fs, nfft=1200)
    # print(test.shape)

    mindist = 9999999
    for th, source in enumerate(sources):
        n = len(source)
        m = len(test)

        if n < m:
            dist = (fastDTW(test, source)[0]) / n
            if dist < mindist:
                mindist = dist

            if dist <= limit:
                rtn[0] = 1       # True
                rtn[1] = dist    # DTW Distance
                rtn[2] = th      # ith Chunks
                return

        for i in range(m, n + 1, 20):
            dist = (fastDTW(test, source[i - m:i, :])[0]) / m
            if dist < mindist:
                mindist = dist

            if dist <= limit:
                rtn[0] = 1  # True
                rtn[1] = dist  # DTW Distance
                rtn[2] = th  # ith Chunks
                return

    rtn[0] = 0   # True
    rtn[1] = mindist  # DTW Distance
    rtn[2] = -1  # ith Chunks
