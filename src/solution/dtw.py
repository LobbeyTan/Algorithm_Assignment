import multiprocessing
import numpy as np
import src.constant
from scipy.io import wavfile
from python_speech_features import mfcc
from os import listdir
from pydub import AudioSegment
from pydub.silence import split_on_silence


# Get the minimum cost from the adjacent cells
# Return index position or minimum cost value
def __getMin(cost, indexes, getVal=False):
    # Get the cost of the adjacent cells (i-1, j-1), (i-1, j), (i, j-1) from cost matrix
    costs = [cost[i, j] if i >= 0 and j >= 0 else np.nan for i, j in indexes]

    # Check whether the costs array is all nan
    if all(np.isnan(costs)):
        # Return not found 0(value) or (-1, -1)[position]
        return 0 if getVal else (-1, -1)

    # Return the index of the minimum values in costs ignoring NaNs
    idx = np.nanargmin(costs)

    # Return minimum costs if gatVal=true, else return minimum indexes
    if getVal:
        return costs[idx]

    return indexes[idx]


# Calculate the cost / distance
def __distance(a, b):
    if a.ndim == b.ndim == 0:  # if array dimensions=0
        return abs(a - b)

    # np.linalg.norm calculate matrix norms
    # np.atleast_1d convert inputs to arrays with at least one dimension
    return np.linalg.norm(np.atleast_1d(a) - np.atleast_1d(b), 1)


# reduce the size of array with the factor of 2
def __reduceByHalf(x):
    return [(x[i] + x[1 + i]) / 2 for i in range(0, len(x) - len(x) % 2, 2)]


# Refinement and identify the cells included for next resolution
# Refine the warping path projected from a lower resolution through local adjustments of the warp path
def __expandResWindow(lowResPath, X, Y, radius):
    path_ = set(lowResPath)
    for i, j in lowResPath:
        for a, b in ((i + a, j + b)
                     for a in range(-radius, radius + 1)
                     for b in range(-radius, radius + 1)):
            path_.add((a, b))

    window_ = set()
    for i, j in path_:
        # add a,b to i*2,j*2 and right, up and upright corner of i*2, j*2
        for a, b in ((i * 2, j * 2), (i * 2, j * 2 + 1),
                     (i * 2 + 1, j * 2), (i * 2 + 1, j * 2 + 1)):
            window_.add((a, b))

    window = []
    start_j = 0
    for i in range(0, len(X)):  # horizontally
        new_start_j = None
        for j in range(start_j, len(Y)):  # vertically
            if (i, j) in window_:  # if true, add i,j to window[] and set new start to j
                window.append((i, j))
                if new_start_j is None:
                    new_start_j = j
            elif new_start_j is not None:  # if there is new start break loop
                break
        start_j = new_start_j

    return window


# DTW algorithm use to calculate distance and warping path
def dtw(series_1, series_2, window=None):
    # length of series_1
    m = len(series_1)
    # length of series_2
    n = len(series_2)

    # If window is None
    if window is None:
        window = [(i, j) for i in range(m) for j in range(n)]  # window size=m*n

    cost = np.full(shape=(m, n), fill_value=np.nan)  # create new matrix with size (m, n)

    # Fill up the cost matrix
    for i, j in window:
        # Get the adjacent minimum
        adj_min = __getMin(cost, [(i - 1, j), (i, j - 1), (i - 1, j - 1)], getVal=True)
        # Calculate cost at (i, j)
        cost[i, j] = __distance(series_1[i], series_2[j]) + adj_min

    # Set (i, j) to the bottom right corner
    (i, j) = (m - 1, n - 1)
    path = []
    distance = 0

    # Obtain the warping path from bottom right corner to top left corner
    while i >= 0 or j >= 0:
        # Storing the warping path
        path += [(i, j)]
        # Calculate the distance
        distance += cost[i, j]
        # Get the position of cell which is has minimum cost between left, top and top left bottom corner
        (i, j) = __getMin(cost, [(i - 1, j), (i, j - 1), (i - 1, j - 1)])

    # Calculate averge diatance
    distance /= len(path)

    path.reverse()
    return distance, path


# FastDTW algorithms
def fastDTW(X, Y, radius=1):
    # Initialize the minimum size of the shrunken matrix
    minSize = radius + 2
    m = len(X)
    n = len(Y)

    # Base case
    # If the size of current x and y series less than minSize
    if m < minSize or n < minSize:
        return dtw(X, Y)

    # Shrunk x and y series by half
    shrunkX = __reduceByHalf(X)
    shrunkY = __reduceByHalf(Y)

    # Get the distance and low resolution warping path from dtw
    distance, lowResPath = fastDTW(shrunkX, shrunkY, radius)

    # Get the windows(cells included for analysis) for the next resolution
    window = __expandResWindow(lowResPath, X, Y, radius)

    # Run DTW and return distance and warping path of current resolution
    return dtw(X, Y, window)


# Function to split the audio file into chunks
def splitAudio(path, filename, min_silence_len=100, silence_thresh=-50):
    samples = AudioSegment.from_wav(f"{path}{filename}")

    # split the audio by silence
    audio_chunks = split_on_silence(samples, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    print(len(audio_chunks))

    # Export each audio chunks
    for i, chunk in enumerate(audio_chunks):
        out_file = f"{src.constant.split}/{filename}{i}.wav"
        print("exporting", out_file)
        chunk.export(out_file, format="wav")


# Get all the audio chunks and make it as an array
def getSources():
    path = src.constant.split
    sources = []

    # Find file in the directory
    for fname in listdir(path):
        fs, data = wavfile.read(f"{path}/{fname}")
        # Apply mfcc feature extraction on each chunks file
        sources.append(mfcc(data, fs, nfft=1200))
    return sources


# A function to run the DTW analysis
def runDTW(testWord: str, rtn: multiprocessing.Array, limit=95):
    # Get audio chunks as an array
    sources = getSources()

    try:
        fs, test = wavfile.read(f"{src.constant.test}/{testWord}")
        # print(test.shape)
    except FileNotFoundError:
        print(f"File not found: no audio file named {testWord}")
        rtn[0] = 0  # False
        rtn[1] = -1  # DTW Distance
        rtn[2] = -1  # ith Chunks
        return rtn

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
                rtn[0] = 1  # True
                rtn[1] = dist  # DTW Distance
                rtn[2] = th  # ith Chunks
                return

        for i in range(m, n + 1, 20):  # Step size = 20
            dist = (fastDTW(test, source[i - m:i, :])[0]) / m
            if dist < mindist:
                mindist = dist

            if dist <= limit:
                rtn[0] = 1  # True
                rtn[1] = dist  # DTW Distance
                rtn[2] = th  # ith Chunks
                return

    rtn[0] = 0  # True
    rtn[1] = mindist  # DTW Distance
    rtn[2] = -1  # ith Chunks
