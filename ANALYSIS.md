# Assignment 4 — Analysis

The public fixtures were checked against the functions, and the program entry point was also checked with JSON-lines input. The student fixtures are in `tests/student/student-test.json`. The final public-fixture check had 44 cases and 0 mismatches. The student fixture check had 10 cases and 0 mismatches.

## Algorithm explanations

### 1. LCS — longest common subsequence

I use a two-dimensional DP table `L`. `L[i][j]` is the length of the longest common subsequence of the first `i` characters of `a` and the first `j` characters of `b`. The extra first row and first column are initialized to zero, because an empty string has an LCS of length zero with any string.

The table is filled from top to bottom and left to right. If `a[i-1] == b[j-1]`, the characters can extend a common subsequence, so `L[i][j] = L[i-1][j-1] + 1`. Otherwise, I take the larger result from the cell above or the cell on the left. These cells are already calculated because of the filling order.

After filling the table, I reconstruct one sequence by starting at `(n, m)`. Equal characters are added to the answer and both indexes move diagonally. If they are different, I move to the neighbor with the larger DP value. When the values are equal, I move up. I reverse the collected characters at the end. This tie rule gives `AC` for the public `ABC` / `BAC` example.

The recurrence is correct because an optimal subsequence either uses the two equal final characters, or (when they differ) must omit at least one of them. The recurrence checks exactly these possibilities. Reconstruction follows the same choices backwards, so it returns a common subsequence whose length is `L[n][m]`.

Time complexity is `O(n*m)` and memory complexity is `O(n*m)` for the DP table. The reconstruction itself takes `O(n+m)` time and uses at most `O(n+m)` output space.

Boundary test: `a=""`, `b="abc"` must return length `0` and an empty sequence. The `lcs-interleaved` student test checks reconstruction on two different strings with characters in a different order.

### 2. Merge — optimal merge order

`dp[l][r]` stores the minimum cost to merge the consecutive items from index `l` through index `r`. A single item needs no merge, so every diagonal cell `dp[i][i]` is zero. I build a prefix-sum array so the sum of any interval can be found in constant time: `prefix[r+1] - prefix[l]`.

For every interval length from `2` to `n`, I try every split point `k` between `l` and `r-1`. The cost of choosing this split is the best cost for the left interval plus the best cost for the right interval plus the sum of the whole interval. The smaller candidate is stored in `dp[l][r]`, and `split[l][r]` remembers the split point.

Shorter intervals are processed first, so both subproblems are ready before a larger interval uses them. Reconstruction recursively visits the left and right parts and then appends `[l, k, k+1]`, which records the merge after its two parts have been prepared. When costs tie, the loop updates on `<=`; because split points are visited in increasing order, the last (largest) split point is kept.

The recurrence considers every possible last split of an interval. Any valid merge plan has one such split, and its two subplans must themselves be optimal; otherwise replacing one with a cheaper subplan would improve the whole plan. Therefore taking the minimum over all splits gives the optimal cost.

Time complexity is `O(n^3)`: there are `O(n^2)` intervals and up to `O(n)` split points per interval. Memory complexity is `O(n^2)` for `dp` and `split`, plus `O(n)` for prefix sums and the plan. For an empty input the function returns cost `0` and an empty plan.

Boundary tests: empty/single-item inputs need no merges. `merge-zero` checks that equal-cost choices still produce a deterministic plan.

### 3. Tree — maximum-weight independent set

The input tree is stored as an adjacency list. I root it at vertex `0` and use DFS to calculate two DP values for each vertex `u`:

- `dp[u][0]`: best weight in the subtree when `u` is not selected.
- `dp[u][1]`: best weight in the subtree when `u` is selected.

If `u` is not selected, each child can either be selected or not, so I add `max(dp[v][0], dp[v][1])` for every child. If `u` is selected, none of its children can be selected, so I add only `dp[v][0]`. The base values before processing children are `0` for excluding `u` and `weights[u]` for including it.

DFS visits a child before its parent finishes its calculation. Therefore all child DP values are ready when the parent uses them. The answer is the larger of the two values at the root. A second traversal reconstructs the selected vertices: if the parent was selected, the current vertex must be excluded. Otherwise, I select the current vertex when its include value is positive and at least as good as its exclude value. This makes the positive tie in `tree-tie` select vertex `0`, while zero or negative-only choices can remain unselected.

The recurrence is correct because an independent set either contains `u` or does not contain `u`. In the first case all children are excluded; in the second case each child subtree can independently use its better state. These cases cover every valid independent set.

Time complexity is `O(n)` because every vertex and edge is visited a constant number of times. The adjacency list and DP arrays use `O(n)` memory; the recursive DFS also uses `O(h)` call-stack space, where `h` is the tree height.

Boundary tests: an empty tree returns zero and no selected vertices; all-negative weights should select nothing. The `tree-star` and `tree-chain` student tests check reconstruction on two different tree shapes.

### 4. Naive string search

I check every possible starting index `i` where the pattern can fit. For each start, index `j` compares `text[i+j]` with `pattern[j]` from left to right. If a character differs, the inner loop stops and the next starting position is checked. If all pattern characters match, `i` is added to the result.

The outer loop examines every possible alignment, so no occurrence can be skipped. A match is reported only after all pattern characters match. Moving the start by one also preserves overlapping matches. An empty pattern is handled separately and matches at all `n+1` boundaries.

The worst-case time is `O((n-m+1)*m)`, usually written as `O(n*m)`, and the extra working memory is `O(1)` apart from the output positions. If `m > n`, the answer is empty.

The `naive-word` student test checks that the algorithm reports both occurrences of a pattern in a word.

### 5. KMP — Knuth–Morris–Pratt

First I build the LPS array. `lps[i]` is the length of the longest proper prefix of `pattern[0:i+1]` that is also a suffix of that substring. The variable `length` stores the current candidate prefix length. When characters match, the candidate grows. On a mismatch, I use `lps[length-1]` to fall back to a shorter candidate without restarting from the beginning. If no candidate remains, the current LPS value is zero.

During the search, `i` is the current text index and `j` is the current pattern index. On a match both increase. When `j == m`, I record `i-j` and fall back using `lps[j-1]`, which allows overlapping matches. On a mismatch, I move `j` to its LPS fallback if possible; otherwise I advance `i`.

The LPS value preserves the longest prefix that could still match after a mismatch. Characters already known to match are not compared again unnecessarily. This is why the text index does not move backwards and the algorithm finds all matches, including overlaps.

Building LPS takes `O(m)` time. Searching takes `O(n)` time, so total time is `O(n+m)`. The LPS array uses `O(m)` extra memory, excluding output. Empty patterns return all `n+1` boundaries.

The `kmp-long-fallback` student test checks fallback after a long partial match.

### 6. Rabin–Karp (RK)

I calculate a rolling hash for the pattern and the first text window. The required base is `31` and the modulus is `101`. The value `h = 31^(m-1) mod 101` is used to remove the first character of the old window. When the window moves one position, I subtract the outgoing character contribution, multiply by the base, add the incoming character, and take the modulus.

For each window, I compare its hash with the pattern hash. A hash match is only a candidate: I compare the actual text slice with the pattern before reporting a position. This verification is important because different strings can have the same hash. The hash update is constant time per window.

The rolling hash lets the algorithm avoid comparing every character at every position when hashes differ. Verification ensures correctness even when a collision occurs. Empty patterns and patterns longer than the text are handled separately.

Hash calculation and rolling through all windows take `O(n+m)` time. If `c` windows have the same hash as the pattern, character verification can add `O(c*m)` time. Thus the candidate-sensitive bound is `O(n+m+c*m)`, with worst case `O(n*m)`. Extra working memory is `O(1)` apart from output.

The `rk-sentence` student test checks that the rolling window locates a pattern after spaces and other characters.

### 7. Suffix array and Kasai LCP

#### Suffix array (doubling)

The suffix array stores every starting index of the text, sorted by the suffix that starts there. Initially, each suffix is ranked by its first character. In each doubling round, I sort suffix indexes by a pair: the rank at the current position and the rank `k` characters later. If the second part is outside the string, I use `-1`, which sorts it before a real rank. After sorting, I assign new ranks to distinct pairs and double `k`.

Each round sorts prefixes twice as long as the previous round. When every suffix has a unique rank, the array is fully sorted and the loop can stop. The suffixes are represented by indexes rather than copied substrings.

There are `O(log n)` rounds. Each round uses Python's comparison sort on `n` indexes, so this implementation takes `O(n log^2 n)` time. The suffix array and rank arrays use `O(n)` memory, excluding sorting implementation overhead.

#### Kasai LCP

Kasai builds the inverse rank array, where `rank[i]` is the position of suffix `i` in the suffix array. For each text position `i`, it compares suffix `i` with the suffix immediately before it in suffix-array order. The variable `h` stores the common-prefix length carried from the previous text position. After storing the LCP, I decrease `h` by one, because removing the first character can reduce the common prefix by at most one.

The previous suffix is already known from the inverse rank array. Carrying `h` avoids repeating comparisons from the beginning, which makes the total number of character comparisons linear. Kasai takes `O(n)` time and `O(n)` extra memory.

The largest LCP value is the longest repeated substring length. Its associated suffix-array position gives the starting index for the substring. If several maximum values tie, the first maximum in the LCP array is used.

The `suffix-mississippi` student test checks suffix ordering and repeated groups of characters.

### 8. Aho–Corasick

I insert all patterns into a trie. Each trie node represents a prefix, and each dictionary entry maps a character to the next node. The `terminal` array stores the final node for each original pattern. Keeping one terminal entry per input pattern preserves duplicate patterns and their output positions.

Failure links are built with BFS. A failure link points to the longest proper suffix of the current trie prefix that is also a trie prefix. For each child edge, I follow failure links until I find a state with the needed character or reach the root. BFS processes shallower nodes first, so the failure link target is already known.

For each text, I start from the root with a fresh `visits` array. Each character follows trie edges; on a missing edge I follow failure links. I increment the visit count of the state reached after consuming the character. After scanning the text, I process trie nodes in reverse BFS order and add each node's visits to its failure parent. This propagates occurrences to suffix-pattern states. Finally, I read the visit count at each original pattern's terminal node. Duplicate patterns therefore receive the same count, in their original input order. Empty patterns are handled separately and occur at `len(text)+1` boundaries.

The state reached after each character represents the longest suffix of the processed text that is also a trie prefix. Failure links preserve shorter possible suffixes. Propagating counts from each state to its failure ancestors counts patterns that end as suffixes of a longer matched prefix. Resetting `state` and `visits` for every text prevents counts from leaking between texts.

Let `S` be the number of trie nodes, `P` the number of input patterns, and `T` the total length of the texts being scanned. Trie insertion is linear in the total pattern length. Failure construction follows failure chains for trie edges; with this sparse-dictionary implementation, a conservative bound is `O(S * L)`, where `L` is the maximum pattern length. For each text, scanning is amortized `O(text length)`, propagation is `O(S)`, and producing the answer is `O(P)`. Memory is `O(S+P)` for the trie, failure links, terminal indexes and counters, excluding the input and output.

The `aho-mixed-overlaps` and `aho-prefix-chain` student tests check overlapping matches, suffix propagation, prefix relationships and fresh counters for each text.

## Own tests

I created a separate set of 10 student tests. I chose different input strings, tree shapes, pattern examples and array values from the examples in the public fixtures. The tests cover the main algorithm behavior and several non-trivial cases. I ran each fixture against the implementation; all expected results matched the actual results.

| Test | Input / fixture | Expected result | Actual result | Defect or boundary checked |
|---|---|---|---|---|
| LCS interleaved | `lcs-interleaved`: `algorithm` / `logarithm` | length 7, `lgrithm` | PASS | Reconstructing a subsequence when matching characters are separated |
| Merge four items | `merge-four-items`: `[5,2,8,3]` | cost 36, three-step plan | PASS | DP over several possible split points |
| Tree star | `tree-star`: root with four leaves | weight 22, `[1,2,3,4]` | PASS | Choosing multiple non-adjacent children instead of the root |
| Tree chain | `tree-chain`: five vertices | weight 18, `[1,3]` | PASS | Independent-set choices along a longer path |
| Naive word | `mississippi` / `issi` | positions `[1,4]` | PASS | Finding more than one occurrence |
| KMP long fallback | `abcxabcdabxabcdabcdabcy` / `abcdabcy` | position `[15]` | PASS | Reusing prefix information after mismatches |
| RK sentence | `the quick brown fox jumps` / `fox` | position `[16]` | PASS | Searching for a pattern inside text containing spaces |
| Suffix mississippi | `mississippi` | SA, LCP and `issi` | PASS | Sorting suffixes with repeated character groups |
| Aho mixed overlaps | patterns `aba`, `ba`, `a`, `bab` | `[[3,3,4,2],[1,2,2,1],[0,0,0,0]]` | PASS | Overlapping matches and suffix-pattern counting |
| Aho prefix chain | patterns `a`, `ab`, `abc`, `bc` | `[[2,2,2,2],[1,1,1,1],[0,0,0,0]]` | PASS | Prefix relationships and resetting counts for each text |

### Additional randomized cross-checks

Besides the named fixtures, I compared the implementations with simple reference solutions on generated small inputs:

- LCS: 1,000 random pairs of short strings, checking both the optimal length and that the returned sequence is a subsequence of both inputs.
- Tree DP: 900 random trees with up to 9 vertices, comparing the result with exhaustive checking of every vertex subset and validating that the selected set contains no adjacent vertices.
- Naive, KMP and RK: 500 random text/pattern pairs, comparing all three position lists with direct substring checking.
- Suffix array: 500 random non-empty strings, comparing suffix order, adjacent LCP values and the selected repeated substring with a direct reference implementation.
- Aho–Corasick: 500 random dictionaries and text batches, comparing every pattern count with direct occurrence counting.

All of these cross-checks passed. They are additional development checks, not a replacement for the assignment's published tests.

## Search comparison: Naive, KMP and Rabin–Karp

I used the same text and pattern for all three algorithms in each experiment. The sizes were `n = 500, 1500, 3000`, with `m = n/4`. For each size I tested two inputs:

- Random: lowercase English letters selected uniformly with a fixed seed. The pattern was copied from one random position in the generated text.
- Repetitive: the text was all `a`; the pattern was `a` repeated `m-1` times followed by `b`. This is a difficult near-match for Naive because many windows match almost the whole pattern before failing at the last character.

Seeds were `20261607`, `20262607`, and `20264107` for the random cases at the three sizes, and `20271607`, `20272607`, and `20274107` for the repetitive cases. I checked the returned positions against a direct `startswith` reference calculation before recording times. Each algorithm/input pair had one untimed warm-up followed by three timed runs. Times are milliseconds, measured around the function call only; importing Python modules and generating input were outside the timed section. The Python interpreter was already running, so there was no compilation step.

| Case | n | m | Seed | Algorithm | Run 1 (ms) | Run 2 (ms) | Run 3 (ms) | Median (ms) | Correct |
|---|---:|---:|---:|---|---:|---:|---:|---:|---|
| Random | 500 | 125 | 20261607 | Naive | 0.041 | 0.042 | 0.041 | 0.041 | Yes |
| Random | 500 | 125 | 20261607 | KMP | 0.067 | 0.062 | 0.109 | 0.067 | Yes |
| Random | 500 | 125 | 20261607 | RK | 0.232 | 0.073 | 0.514 | 0.232 | Yes |
| Random | 1500 | 375 | 20262607 | Naive | 1.077 | 0.197 | 0.645 | 0.645 | Yes |
| Random | 1500 | 375 | 20262607 | KMP | 0.309 | 0.242 | 0.295 | 0.295 | Yes |
| Random | 1500 | 375 | 20262607 | RK | 0.222 | 0.275 | 0.224 | 0.224 | Yes |
| Random | 3000 | 750 | 20264107 | Naive | 0.410 | 0.339 | 0.309 | 0.339 | Yes |
| Random | 3000 | 750 | 20264107 | KMP | 0.563 | 0.512 | 0.399 | 0.512 | Yes |
| Random | 3000 | 750 | 20264107 | RK | 0.515 | 0.480 | 0.476 | 0.480 | Yes |
| Repetitive | 500 | 125 | 20271607 | Naive | 1.646 | 1.900 | 1.467 | 1.646 | Yes |
| Repetitive | 500 | 125 | 20271607 | KMP | 0.071 | 0.070 | 0.070 | 0.070 | Yes |
| Repetitive | 500 | 125 | 20271607 | RK | 0.068 | 0.068 | 0.068 | 0.068 | Yes |
| Repetitive | 1500 | 375 | 20272607 | Naive | 16.210 | 17.468 | 18.618 | 17.468 | Yes |
| Repetitive | 1500 | 375 | 20272607 | KMP | 0.268 | 0.235 | 0.254 | 0.254 | Yes |
| Repetitive | 1500 | 375 | 20272607 | RK | 0.222 | 0.220 | 0.263 | 0.222 | Yes |
| Repetitive | 3000 | 750 | 20274107 | Naive | 92.848 | 90.160 | 85.464 | 90.160 | Yes |
| Repetitive | 3000 | 750 | 20274107 | KMP | 0.540 | 0.530 | 0.484 | 0.530 | Yes |
| Repetitive | 3000 | 750 | 20274107 | RK | 0.486 | 0.512 | 0.500 | 0.500 | Yes |

On random text, Naive was competitive because most windows fail early. On the repetitive near-match, Naive became much slower as the input grew, because it compared almost all `m` characters at almost every starting position. KMP stayed close to linear growth because it reuses the LPS information. RK was also fast on these measurements, but it still verifies matching hashes, and the small modulus can produce many candidates on other inputs. These measurements are observations for these particular inputs and this environment; they do not prove the asymptotic complexity.

## Sources and AI assistance

I used the assignment README and public test fixtures as the main sources for the input/output contract. I also used the Python standard library documentation for basic language features such as lists, dictionaries, sorting and `deque`.

I used ChatGPT to explain algorithm concepts, help me understand problems and error messages, and give hints about possible ways to debug them. I wrote the algorithm implementations myself and checked my work by running the public tests, my own student tests and additional comparison tests. I used the explanations as learning support, not as a replacement for testing or understanding the code.

