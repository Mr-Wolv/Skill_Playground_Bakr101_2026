---
name: computer-science-foundations
description: Algorithms, data structures, complexity analysis, automata, compilers, OS, memory, concurrency
---

# Computer Science Foundations

Practical coverage of core computer science concepts grounded in real-world application.

## When to use

- Analyzing algorithm efficiency for a performance-sensitive feature
- Understanding memory management in your language/runtime
- Debugging concurrency issues (races, deadlocks)
- Making data structure choices with sound reasoning

## Instructions

1. **Algorithm analysis** — evaluate time complexity (Big O: O(1), O(log n), O(n), O(n log n), O(n²), O(2ⁿ)) and space complexity
2. **Data structure selection** — choose wisely:
   - **Array**: fast indexed access, slow insert/delete
   - **HashMap**: fast key lookup, unordered, O(1) average
   - **TreeMap/BST**: ordered keys, O(log n) operations
   - **Set**: uniqueness checks
   - **Stack/Queue**: LIFO/FIFO access patterns
   - **Heap**: priority queue operations
3. **Memory management** — stack vs heap allocation, garbage collection strategies (mark-sweep, generational, reference counting), memory leaks and how to detect them
4. **Concurrency** — threads vs processes, mutexes, semaphores, race conditions, deadlock prevention (lock ordering, timeout), atomics, lock-free data structures

## Practical applications

| Concept | Use case |
|---------|----------|
| B-tree / B+ tree | Database indexes |
| Hash table | Caches, lookup tables |
| LRU cache | Memory-constrained caching |
| Trie | Autocomplete, prefix matching |
| Bloom filter | Probabilistic membership tests |
| Binary search | Fast lookup in sorted data |
| Merge sort / Quick sort | General-purpose sorting |
| Dijkstra / A* | Pathfinding, network routing |

## Anti-patterns

- Premature optimization (pick the right data structure for the access patterns, not for theoretical maximum performance)
- Ignoring cache locality (arrays are faster than linked lists for iteration due to CPU cache)
- Over-engineering (a simple array with linear search is fine for N < 100)
- Using threads for everything (async/event-driven can be simpler for I/O-bound work)
