from collections import deque

"""Implement algorithm bodies. See docs/guide/CONTRACTS.md; inputs and outputs are dictionaries."""
def lcs(request):
    x, y = request["a"], request["b"]
    n, m = len(x), len(y)
    L = [[0] * (m + 1) for _ in range(n + 1)]
    sequence = ""
    current_max = 0
        
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if x[i - 1] == y[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
                if L[i][j] > current_max:
                    current_max = L[i][j]
                    sequence += x[i - 1]
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])
                current_max = max(current_max, L[i][j])
        
    return {"length": L[n][m], "sequence": sequence}    



def merge(request):
    sizes = request["sizes"]
    n = len(sizes)

    if n == 0:
        return {"cost": 0, "plan": []}

    dp = [[0] * n for _ in range(n)]
    split = [[-1] * n for _ in range(n)]

    prefix = [0] * (n + 1)

    for i in range(n):
        prefix[i + 1] = prefix[i] + sizes[i]

    for length in range(2, n + 1):
        for l in range(n - length + 1):
            r = l + length - 1

            dp[l][r] = float('inf')
            interval_sum = prefix[r + 1] - prefix[l]

            for k in range(l, r):
                cost = dp[l][k] + dp[k + 1][r] + interval_sum

                if cost <= dp[l][r] or (cost == dp[l][r] and (split[l][r] == -1 or k < split[l][r])):
                    dp[l][r] = cost
                    split[l][r] = k

    plan = []

    def reconstruct(l, r):
        if l == r:
            return

        k = split[l][r]

        reconstruct(l, k)
        reconstruct(k + 1, r)

        plan.append([l, k, k + 1])

    reconstruct(0, n - 1)

    return {
        "cost": dp[0][n - 1],
        "plan": plan
    }



def tree(request):
    n = request["n"]
    edge = request["edges"]
    weights = request["weights"]

    if n == 0:
        return {"weight": 0, "selected": []}
    
    tree = [[] for _ in range(len(edge) + 1)]
    for u, v in edge:
        tree[u].append(v)
        tree[v].append(u)
    
    visited = [False] * len(tree)
    dp = [[] for _ in range(len(edge) + 1)]

    def dfs(u):
        visited[u] = True
        dp[u] = [0, weights[u]]
        for v in tree[u]:
            if not visited[v]:
                dfs(v)
                dp[u][0] += max(dp[v][0], dp[v][1])
                dp[u][1] += dp[v][0]
    
    def sequence_def(i, side):
        visited[i] = True
    
        if side == 1:
            for v in tree[i]:
                if not visited[v]:
                    sequence_def(v, 0)
    
        else:
            if dp[i][1] > dp[i][0]:
                sequence.append(i)
                for v in tree[i]:
                    if not visited[v]:
                        sequence_def(v, 1)
            else:
                for v in tree[i]:
                    if not visited[v]:
                        sequence_def(v, 0)
    
    dfs(0)
    
    cost = max(dp[0][0], dp[0][1])
    visited = [False] * len(weights)
    sequence = []
    
    sequence_def(0, 0)
    
    return {"weight": cost, "selected": sequence}



def naive(request):
    text = request["text"]
    pattern = request["pattern"]

    m = len(pattern)
    n = len(text)
    positions = []

    if n < m or m == 0:
        return {"positions": [i for i in range(n+1)] if m == 0 else []}

    for i in range(n - m + 1):
        for j in range(m):
            if text[i + j] != pattern[j]:
                break
        if j == m - 1 and text[i + j] == pattern[j]:
            positions.append(i)

    return {"positions": positions}

def kmp(request):
    text, pattern = request["text"], request["pattern"]
    n = len(text)
    m = len(pattern)

    if m == 0:
        return {"positions": list(range(n + 1))}

    if m > n:
        return {"positions": []}

    def build_lps(pattern):
        m = len(pattern)
        lps = [0] * m

        length = 0
        i = 1

        while i < m:
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1

            elif length != 0:
                length = lps[length - 1]

            else:
                lps[i] = 0
                i += 1
        return lps

    lps = build_lps(pattern)

    positions = []

    i = 0 
    j = 0 

    while i < n:

        if text[i] == pattern[j]:
            i += 1
            j += 1

        if j == m:
            positions.append(i - j)
            j = lps[j - 1]

        elif i < n and text[i] != pattern[j]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1

    return {"positions": positions}

def rk(request):
    text, pattern = request["text"], request["pattern"]
    n = len(text)
    m = len(pattern)

    if m == 0:
        return {"positions": list(range(n + 1))}

    if m > n:
        return {"positions": []}

    base = 31
    mod = 101

    hash_pattern = 0
    hash_window = 0

    h = pow(base, m - 1, mod)

    for i in range(m):
        hash_pattern = (hash_pattern * base + ord(pattern[i])) % mod
        hash_window = (hash_window * base + ord(text[i])) % mod

    positions = []

    for i in range(n - m + 1):

        if hash_pattern == hash_window:
            if text[i:i + m] == pattern:
                positions.append(i)

        if i < n - m:
            hash_window = (
                (hash_window - ord(text[i]) * h) * base
                + ord(text[i + m])
            ) % mod

    return {"positions": positions}



def suffix(request):

    def build_sa(text):
        n = len(text)
        sa = list(range(n))
        rank = [ord(c) for c in text]

        k = 1

        while k < n:
            sa.sort(key=lambda i: (
                rank[i],
                rank[i + k] if i + k < n else -1
            ))

            new_rank = [0] * n

            for i in range(1, n):
                prev = sa[i - 1]
                curr = sa[i]

                prev_pair = (
                    rank[prev],
                    rank[prev + k] if prev + k < n else -1
                )

                curr_pair = (
                    rank[curr],
                    rank[curr + k] if curr + k < n else -1
                )

                new_rank[curr] = new_rank[prev]

                if prev_pair != curr_pair:
                    new_rank[curr] += 1

            rank = new_rank

            if rank[sa[-1]] == n - 1:
                break

            k *= 2

        return sa

    def kasai(text, sa):
        n = len(text)
        rank = [0] * n

        for i in range(n):
            rank[sa[i]] = i

        lcp = [0] * n
        h = 0

        for i in range(n):
            r = rank[i]

            if r == 0:
                h = 0
                continue

            j = sa[r - 1]

            while i + h < n and j + h < n:
                if text[i + h] != text[j + h]:
                    break
                h += 1

            lcp[r] = h

            if h > 0:
                h -= 1

        return lcp

    text_glob = request["text"]

    if len(text_glob) == 0:
        return {
            "sa": [],
            "lcp": [],
            "repeated": ""
        }

    sa = build_sa(text_glob)
    lcp = kasai(text_glob, sa)

    best = max(lcp)
    pos = lcp.index(best)

    repeated = text_glob[sa[pos]:sa[pos] + best]

    return {
        "sa": sa,
        "lcp": lcp,
        "repeated": repeated
    }



def aho(request):

    patterns = request["patterns"]
    texts = request["texts"]

    trie = [{}]
    terminal = []

    for pattern in patterns:
        state = 0

        for ch in pattern:
            if ch not in trie[state]:
                trie[state][ch] = len(trie)
                trie.append({})

            state = trie[state][ch]

        terminal.append(state)

    fail = [0] * len(trie)

    queue = deque()
    order = [0]

    for ch, child in trie[0].items():
        fail[child] = 0
        queue.append(child)

    while queue:
        v = queue.popleft()

        for ch, child in trie[v].items():

            f = fail[v]

            while f != 0 and ch not in trie[f]:
                f = fail[f]

            if ch in trie[f]:
                fail[child] = trie[f][ch]
            else:
                fail[child] = 0

            queue.append(child)
            order.append(child)

    results = []

    for text in texts:

        state = 0
        visits = [0] * len(trie)

        for ch in text:

            while state != 0 and ch not in trie[state]:
                state = fail[state]

            if ch in trie[state]:
                state = trie[state][ch]

            visits[state] += 1

        for v in reversed(order[1:]):
            visits[fail[v]] += visits[v]

        answer = []

        for i, pattern in enumerate(patterns):
            if pattern == "":
                answer.append(len(text) + 1)
            else:
                answer.append(visits[terminal[i]])

        results.append(answer)

    return {"counts" : results}

