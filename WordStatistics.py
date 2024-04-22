from math import copysign, ceil

def sign(x):
    if x == 0:
        return 0.0
    return copysign(1.0, x)

def signFromBool(b):
    return 1 if b else -1

"""
Represents an individual character along with a sign. Uses the inherent
ordering on the type of self.char along with the implied ordering of the
type with the negative sign.
self.char -> Symbol representation of the Letter.
self.sign -> True if the Letter is positive, False if the Letter is negative.
"""
class Letter:

    def __init__(self, char, sign=True):
        self.char = char
        self.sign = sign

    def __str__(self):
        if not self.sign:
            return f"(-{str(self.char)})"
        else:
            return str(self.char)

    def __repr__(self):
        return str(self)
    
    def __hash__(self):
        return hash(str(self))
    
    def __sub__(self, other):
        if type(self.char) is str:
            left = signFromBool(self.sign) * (ord(self.char) - ord('a') + 1)
            right = signFromBool(other.sign) * (ord(other.char) - ord('a') + 1)
            return left - right
        return signFromBool(self.sign) * self.char - signFromBool(other.sign) * other.char

    def __le__(self, other):
        if self.sign == other.sign:
            if (self.char == other.char):
                return True
            # True conditions
            # If positive (i.e. not self.sign == False) and self < other == True
            # If negative (i.e. not self.sign == True) and self < other == False
            return (self.char < other.char) ^ (not self.sign)
        else:
            return not self.sign
        
    def __lt__(self, other):
        if self.sign == other.sign:
            if (self.char == other.char):
                return False
            # True conditions
            # If positive (i.e. not self.sign == False) and self < other == True
            # If negative (i.e. not self.sign == True) and self < other == False
            return (self.char < other.char) ^ (not self.sign)
        else:
            return not self.sign
        
    def __gt__(self, other):
        return not (self <= other)
    
    def __ge__(self, other):
        return not (self < other)
    
    def __eq__(self, other):
        return self.sign == other.sign and self.char == other.char

"""
Represents a string of Letters and provides operations for getting the set
of runs within the word (i.e. sequences of weakly ascending Letters). Also
gives functionality for determining if a Word is flattened (i.e. the runs are
in weakly increasing order according to the first Letter of each run).
self.letters -> Array of Letters that the Word represents.
self.weak_runs -> List of lists of Letters representing the Word broken into its weak runs.
            Enumerated on construction.
"""
class Word:

    def __init__(self, letters):
        self.letters = letters
        self.weak_runs = self.getRuns()
        self.peaks = self.getPeaks()

    def __str__(self):
        return "".join([str(x) for x in self.letters])

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.letters)
    
    def getPeaks(self):
        if len(self.letters) == 0:
            return []
        peaks = []
        for i in range(1, len(self.letters) - 1, 1):
            if self.letters[i-1] < self.letters[i] and self.letters[i+1] < self.letters[i]:
                peaks.append(i+1)
        return peaks 
    
    def matchesPeakSet(self, peakset):
        return self.peaks == peakset

    """
    Returns decomposition of word into maximal contiguous weakly increasing subsequences.
    If weak is True, makes the condition strongly increasing.
    """
    def getRuns(self, weak = True):
        if len(self.letters) == 0:
            return []
        else:
            prevLetter = self.letters[0]
        runs = []
        currentRun = [prevLetter]
        for i in range(1, len(self.letters)):
            if weak and prevLetter <= self.letters[i]:
                currentRun.append(self.letters[i])
            elif (not weak) and prevLetter < self.letters[i]:
                currentRun.append(self.letters[i])
            else:
                runs.append(currentRun)
                currentRun = [self.letters[i]]
            prevLetter = self.letters[i]

        runs.append(currentRun)

        return runs

    def getNumRuns(self, weak = True):
        if weak:
            return len(self.weak_runs)
        return len(self.getRuns(weak = False))
    
    """
    For a word of length n, getDeltas returns an array of length n-1
    where the value at position i is self.letters[i+1] - self.letters[i]
    """
    def getDeltas(self):
        if len(self.letters) < 2:
            return []
        deltas = []
        for i in range(0, len(self.letters)-1):
            deltas.append(self.letters[i+1] - self.letters[i])
        return deltas

    """
    If weak_ascents is true consider runs to be weakly increasing. Otherwise strictly increasing.
    If weak us true return True if starts of runs are weakly increasing. Otherwise only return True if they are strictly increasing.
    """
    def isFlattened(self, weak_ascents=True, weak=True):
        if weak_ascents:
            runs = self.weak_runs
        else:
            runs = self.getRuns(weak=False)
        for i in range(len(runs) - 1):
            if weak and not (runs[i][0] <= runs[i+1][0]):
                return False
            elif (not weak) and not (runs[i][0] < runs[i+1][0]):
                return False

        return True
    
    def isPermutation(self):
        letters = set()
        for elm in self.letters:
            letters.add(elm)
        return (len(letters) == len(self.letters)) and (max(letters) - min(letters) + 1 == len(self.letters))
    
    def getOverlappingSymmetricPeaksAndValleys(self):
        deltas = self.getDeltas()
        segments = []
        peak_lengths = []
        segment = [self.letters[0]]
        segment_dir = []
        peak_length = 1
        i = 1
        while i < len(self.letters):
            s = sign(deltas[i-1])
            # either segment is len 1, or direction is not changing
            if len(segment_dir) == 0 or segment_dir[-1] == s:
                segment.append(self.letters[i])
                segment_dir.append(s)
                i += 1
                if s == 0:
                    peak_length += 1
            # if no change, then our peak/valley is longer than 1 elm
            elif s == 0:
                segment.append(self.letters[i])
                peak_length += 1
                i += 1
            # changed direction, copy non-peak/valley elements
            else:
                tail_len = len(segment) - peak_length
                tail = self.letters[i:min(i + tail_len, len(self.letters))]
                segment = segment + tail
                segments.append(segment)
                peak_lengths.append(peak_length)
                peak_length = 1
                # reprime the loop
                i = min(i + tail_len, len(self.letters))
                if i < len(self.letters):
                    s = sign(deltas[i-1])
                    if s == segment_dir[-1] or s == 0:
                        segment = [segment[len(segment) - tail_len - 1]] + tail + [self.letters[i]]
                        if s == 0:
                            peak_length += 1
                    else:
                        segment = [self.letters[i-1], self.letters[i]]
                    segment_dir = [deltas[i-1]]
                    i += 1
                else:
                    segment = []


        if len(segment) > 0:
            segments.append(segment)

        return segments, peak_lengths

    
    """
    If the word is made of symmetric peaks and valleys, return a list containing those
    symmetric peaks and valleys. If the word is not symmetric, then we return our attempt
    at finding the symmetric peaks and valleys.
    """
    def getSymmetricPeaksAndValleys(self):
        deltas = self.getDeltas()
        segments = []
        peak_lengths = []
        segment = [self.letters[0]]
        segment_dir = []
        peak_length = 1
        i = 1
        while i < len(self.letters):
            s = sign(deltas[i-1])
            # either segment is len 1, or direction is not changing
            if len(segment_dir) == 0 or segment_dir[-1] == s:
                segment.append(self.letters[i])
                segment_dir.append(s)
                i += 1
            # if no change, then our peak/valley is longer than 1 elm
            elif s == 0:
                segment.append(self.letters[i])
                peak_length += 1
                i += 1
            # changed direction, copy non-peak/valley elements
            else:
                tail_len = len(segment) - peak_length
                tail = self.letters[i:min(i + tail_len, len(self.letters))]
                segment = segment + tail
                segments.append(segment)
                peak_lengths.append(peak_length)
                segment = []
                peak_length = 1
                # reprime the loop
                i = min(i + tail_len, len(self.letters))
                if i < len(self.letters):
                    segment = [self.letters[i]]
                    segment_dir = []
                    i += 1

        if len(segment) > 0:
            segments.append(segment)

        return segments, peak_lengths

    """
    Returns true if the word is made of symmetric peaks and valleys. It does this by calling
    getSymmetricPeaksAndValleys and checking that each segment is a palindrome.
    """
    def isSymmetric(self, max_peak = None):
        segments, peak_lengths = self.getSymmetricPeaksAndValleys()
        if len(peak_lengths) == 0 or (max_peak is not None and max(peak_lengths) > max_peak):
            return False
        for segment in segments:
            for i in range(0, ceil(len(segment)/2.0)):
                if segment[i] != segment[len(segment) - 1 - i]:
                    return False
        return True
    
    def isCompletelySymmetric(self, max_peak = None):
        segments, peak_lengths = self.getOverlappingSymmetricPeaksAndValleys()
        if len(peak_lengths) == 0 or (max_peak is not None and max(peak_lengths) > max_peak):
            return False
        for segment in segments:
            for i in range(0, ceil(len(segment)/2.0)):
                if segment[i] != segment[len(segment) - 1 - i]:
                    return False
        return True

    def getRunType(self):
        return [len(run) for run in self.weak_runs]

"""
Creates a Word object given an iterable, usually a string.
"""
def makeWord(text):
    return Word([Letter(x) for x in text])


if __name__ == "__main__":
    a = Letter("a")
    neg_a = Letter("a", False)
    b = Letter("b")
    neg_b = Letter("b", False)

    assert str(a) == "a"
    assert str(neg_a) == "(-a)"

    assert a <= b
    assert b <= b
    assert neg_b <= neg_a
    assert not a <= neg_b

    # weak ascents/runs, weak flat
    unflat_word = Word([a, neg_a, b, b, neg_b]) # a | (-a)bb | (-b)
    flat_word = Word([neg_b, neg_a, b, neg_a, a, b, a]) # (-b)(-a)b | (-a)ab | a

    assert str(unflat_word) == "a(-a)bb(-b)"
    assert str(flat_word) == "(-b)(-a)b(-a)aba"

    assert not unflat_word.isFlattened()
    assert flat_word.isFlattened()

    unflat_runs = unflat_word.getRuns()
    assert len(unflat_runs) == 3
    assert str(Word(unflat_runs[0])) == "a"
    assert str(Word(unflat_runs[1])) == "(-a)bb"
    assert str(Word(unflat_runs[2])) == "(-b)"

    flat_runs = flat_word.getRuns()
    assert len(flat_runs) == 3
    assert str(Word(flat_runs[0])) == "(-b)(-a)b"
    assert str(Word(flat_runs[1])) == "(-a)ab"
    assert str(Word(flat_runs[2])) == "a"

    symm_word = Word([a, neg_a, neg_a, a, neg_b, b, b, b, neg_b])
    pavs, pls = symm_word.getSymmetricPeaksAndValleys()
    assert len(pavs) == 2
    assert pavs[0] == [a, neg_a, neg_a, a]
    assert pls[0] == 2
    assert pavs[1] == [neg_b, b, b, b, neg_b]
    assert pls[1] == 3
    assert symm_word.isSymmetric()
    assert not unflat_word.isSymmetric()
    assert not flat_word.isSymmetric()

    comp_symm_word = Word([a, neg_a, neg_b, neg_a, a, a, a, neg_a, neg_b, neg_b, neg_a, a])
    pavs, pls = comp_symm_word.getOverlappingSymmetricPeaksAndValleys()
    assert len(pavs) == 3
    assert pavs[0] == [a, neg_a, neg_b, neg_a, a]
    assert pls[0] == 1
    assert pavs[1] == [neg_b, neg_a, a, a, a, neg_a, neg_b]
    assert pls[1] == 3
    assert pavs[2] == [a, neg_a, neg_b, neg_b, neg_a, a]
    assert pls[2] == 2
    assert comp_symm_word.isCompletelySymmetric()
    assert not symm_word.isCompletelySymmetric()
    assert not unflat_word.isCompletelySymmetric()
    assert not flat_word.isCompletelySymmetric()

    # strong ascents/runs, weak flat
    # unflat_word = Word([a, neg_a, b, b, neg_b]) # a | (-a)b | b | (-b)
    # flat_word = Word([neg_b, neg_a, b, neg_a, a, b, a]) # (-b)(-a)b | (-a)ab | a

    # assert str(unflat_word) == "a(-a)bb(-b)"
    # assert str(flat_word) == "(-b)(-a)b(-a)aba"

    # assert not unflat_word.isFlattened()
    # assert flat_word.isFlattened()

    # unflat_runs = unflat_word.getRuns()
    # assert len(unflat_runs) == 3
    # assert str(Word(unflat_runs[0])) == "a"
    # assert str(Word(unflat_runs[1])) == "(-a)bb"
    # assert str(Word(unflat_runs[2])) == "(-b)"

    # flat_runs = flat_word.getRuns()
    # assert len(flat_runs) == 3
    # assert str(Word(flat_runs[0])) == "(-b)(-a)b"
    # assert str(Word(flat_runs[1])) == "(-a)ab"
    # assert str(Word(flat_runs[2])) == "a"
