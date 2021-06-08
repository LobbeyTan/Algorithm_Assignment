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
    # M is the pattern length
    M = len(pat)

    # N is the text length
    N = len(txt)

    # Create a lps array
    lps = [0] * M

    # Initialize i
    i = 0

    # Call compute LPS array function
    __computeLPSArray(pat, M, lps)

    # Initally is not found
    found = False
    j = 0

    # Loop the whole text
    while j < N:
        # If same character, increment i and j
        if pat[i] == txt[j]:
            j += 1
            i += 1
        # If i reach the last index of pattern
        if i == M:
            i = lps[i - 1]
            # Pattern is found
            found = True
        # If j still in range, but both characters are different
        elif j < N and pat[i] != txt[j]:
            if i != 0:
                i = lps[i - 1]
            else:
                j += 1
    return found


def __computeLPSArray(pat, M, lps):
    # Initalized i, j
    i = 0
    j = 1

    # Run until j >= M
    while j < M:
        # If same characters
        if pat[j] == pat[i]:
            # Store the lps value, increment i & j
            i += 1
            lps[j] = i
            j += 1

        # Not same characters
        else:
            # If has previous value
            if i != 0:
                # Set i to previous lps value
                i = lps[i - 1]

            # If just started
            else:
                # Set lps value to 0
                lps[j] = 0
                j += 1


def getZarr(string, z):
    n = len(string)

    l, r, k = 0, 0, 0
    for i in range(1, n):
        # if i>R nothing matches so we will calculate. Z[i] using naive way
        if i > r:

            # Reset L and R and compute new [L,R] by comparing  str[0..] to str[i..] and get Z[i] (= R-L+1)
            l, r = i, i
            while r < n and string[r - l] == string[r]:
                r += 1
            z[i] = r - l
            r -= 1
        else:
            k = i - l

            # If Z[K] < R-i+1  then there is no prefix substring starting at  str[i]
            # so Z[i] = Z[K] and interval [L,R] remains same
            if z[k] < r - i + 1:
                z[i] = z[k]

            # If Z[K] >= R-i+1 then it is possible to extend the [L,R] interval
            else:
                # set L as i and start matching from str[R]  onwards and get new R
                l = i
                # update interval [L,R] and calculate Z[i] (=R-L+1).
                while r < n and string[r - l] == string[r]:
                    r += 1
                z[i] = r - l
                r -= 1


# A driver code to use Z-algorithm
def match(text, pattern):
    # Concatenate pattern and text with unique character $
    concat = pattern + "$" + text

    # l is the length of concatenated string
    l = len(concat)

    # Initialize Z-array with length l
    z = [0] * l

    # Call Z-algorithm to fill the Z-array
    getZarr(concat, z)

    # Loop the Z-array
    for i in range(l):
        # If pattern found
        if z[i] == len(pattern):
            # Return index of the pattern found
            return i - len(pattern) - 1


# We need a minimum of 16 items in the array to enter the merge sort
# Else the array will only be sorted with Insertion Sort
MIN_MERGE = 16


# calculate minimum Run needed for InsertionSort
def __calcMinRun(n):
    # Returns the minimum length og a run [23 - 64]
    r = 0
    while n >= MIN_MERGE:
        r |= n & 1
        n >>= 1
    return n + r


# InsertionSort
def __insertionSort(arr, left, right):
    # Sort array from left to right
    for i in range(left + 1, right + 1):
        j = i
        # Swap the array if current value < previous value
        while j > left and arr[j] < arr[j - 1]:
            arr[j], arr[j - 1] = arr[j - 1], arr[j]
            j -= 1


# MergeSort
def __merge(arr, l, m, r):
    # Len1 is the left array size
    # Len2 is the right array size
    len1, len2 = m - l + 1, r - m

    # Initialize left and right array
    left, right = [], []

    # Add values to the left array
    for i in range(0, len1):
        left.append(arr[l + i])
    # Add values to the right array
    for i in range(0, len2):
        right.append(arr[m + 1 + i])

    # Initalized i, j to 0 and k to middle index
    i, j, k = 0, 0, l

    # Loop until i or j reach the last index of left or right array
    while i < len1 and j < len2:
        # If current value on the left <= current value on the right
        if left[i] <= right[j]:
            # Set array at index k to current value on the left array
            arr[k] = left[i]
            # Increament i
            i += 1
        else:
            # Set array at index k to current value on the right array
            arr[k] = right[j]
            # Increament j
            j += 1
        # Increament k
        k += 1

    # If has remainded elements in the left array
    while i < len1:
        # Set array at index k to current value on the left array
        arr[k] = left[i]
        # Increament i, k
        k += 1
        i += 1

    # If has remainded elements in the right array
    while j < len2:
        # Set array at index k to current value on the right array
        arr[k] = right[j]
        # Increament j, k
        k += 1
        j += 1


# TimSort
def timSort(arr):
    # n is the length of input array
    n = len(arr)
    # Calculate the minimum runs' size
    minRun = __calcMinRun(n)

    # Sort individual subarrays of runs' size
    for start in range(0, n, minRun):
        end = min(start + minRun - 1, n - 1)
        # Use insertionsort to sort
        __insertionSort(arr, start, end)

    # Get the minimum runs' size
    size = minRun
    while size < n:
        # Pick starting point of the left subarray
        for left in range(0, n, 2 * size):
            # Get the middle index of the array
            mid = min(n - 1, left + size - 1)
            # Get the start index of right array
            right = min((left + 2 * size - 1), (n - 1))
            if mid < right:
                # Use mergeSort to sort
                __merge(arr, left, mid, right)

        # Increase the size by 2
        size = 2 * size
