# Sort the distance from origin to destination go thorough hub in ascending order with cocktail sort
def cocktailSort(distanceWithHub):
    a = list(distanceWithHub.items())
    n = len(a)

    swapped = True
    start = 0
    end = n - 1

    while swapped:

        # reset the swapped flag on entering the loop, because it might be true from a previous iteration.
        swapped = False

        # loop from left to right same as the bubble sort
        for i in range(start, end):
            if a[i][1] > a[i + 1][1]:
                a[i], a[i + 1] = a[i + 1], a[i]
                swapped = True

        # if nothing moved, then array is sorted.
        if not swapped:
            break

        # otherwise, reset the swapped flag so that it can be used in the next stage
        swapped = False

        # move the end point back by one, because item at the end is in its rightful spot
        end = end - 1

        # from right to left, doing the same comparison as in the previous stage
        for i in range(end - 1, start - 1, -1):
            if a[i][1] > a[i + 1][1]:
                a[i], a[i + 1] = a[i + 1], a[i]
                swapped = True

        # increase the starting point, because last stage would have moved next smallest number to rightful spot.
        start = start + 1

    return a


# Search for stopwords using KMP algorithm
def KMPSearch(pat, txt):
    M = len(pat)
    N = len(txt)
    lps = [0] * M
    i = 0

    __computeLPSArray(pat, M, lps)
    found = False
    j = 0

    while j < N:
        if pat[i] == txt[j]:
            j += 1
            i += 1
        if i == M:
            i = lps[i - 1]
            found = True
        elif j < N and pat[i] != txt[j]:
            if i != 0:
                i = lps[i - 1]
            else:
                j += 1
    return found


def __computeLPSArray(pat, M, lps):
    i = 0
    j = 1
    while j < M:
        if pat[j] == pat[i]:
            i += 1
            lps[j] = i
            j += 1
        else:
            if i != 0:
                i = lps[i - 1]

            else:
                lps[j] = 0
                j += 1


def getZarr(string, z):
    n = len(string)

    l, r, k = 0, 0, 0
    for i in range(1, n):

        if i > r:
            l, r = i, i
            while r < n and string[r - l] == string[r]:
                r += 1
            z[i] = r - l
            r -= 1
        else:
            k = i - l

            if z[k] < r - i + 1:
                z[i] = z[k]

            else:
                l = i
                while r < n and string[r - l] == string[r]:
                    r += 1
                z[i] = r - l
                r -= 1


def match(text, pattern):
    concat = pattern + "$" + text
    l = len(concat)
    z = [0] * l
    getZarr(concat, z)
    for i in range(l):
        if z[i] == len(pattern):
            return i - len(pattern) - 1


MIN_MERGE = 16  # We need a minimum of 16 items in the array to enter the merge sort, else the array will only be sorted with Insertion Sort


# calculate minimum Run needed for InsertionSort
def __calcMinRun(n):
    r = 0
    while n >= MIN_MERGE:
        r |= n & 1
        n >>= 1
    return n + r


# InsertionSort
def __insertionSort(arr, left, right):
    for i in range(left + 1, right + 1):
        j = i
        while j > left and arr[j] < arr[j - 1]:
            arr[j], arr[j - 1] = arr[j - 1], arr[j]
            j -= 1


# MergeSort
def __merge(arr, l, m, r):
    len1, len2 = m - l + 1, r - m
    left, right = [], []
    for i in range(0, len1):
        left.append(arr[l + i])
    for i in range(0, len2):
        right.append(arr[m + 1 + i])

    i, j, k = 0, 0, l

    while i < len1 and j < len2:
        if left[i] <= right[j]:
            arr[k] = left[i]
            i += 1

        else:
            arr[k] = right[j]
            j += 1

        k += 1

    while i < len1:
        arr[k] = left[i]
        k += 1
        i += 1

    while j < len2:
        arr[k] = right[j]
        k += 1
        j += 1


# TimSort
def timSort(arr):
    n = len(arr)
    # Calculate the minimum Run needed
    minRun = __calcMinRun(n)

    for start in range(0, n, minRun):
        end = min(start + minRun - 1, n - 1)
        __insertionSort(arr, start, end)

    size = minRun
    while size < n:
        for left in range(0, n, 2 * size):
            mid = min(n - 1, left + size - 1)
            right = min((left + 2 * size - 1), (n - 1))
            if mid < right:
                __merge(arr, left, mid, right)

        size = 2 * size
