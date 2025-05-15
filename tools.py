from collections import Counter

from exceptions import ExcitedSiteswapError, NotValidSiteswapError


def is_valid(
    pattern: list[int] | tuple[int, ...], num_of_object: int | None = None
) -> bool:
    """
    Check if a pattern is valid based on collision and object count.

    Args:
        pattern (list[int] | tuple[int,...]): The pattern to validate.

    Returns:
        bool: `True` if the pattern is valid, `False` otherwise.
    """
    period = len(pattern)

    # Check if the number of objects (balls) is an integer
    if sum(pattern) / period != int(sum(pattern) / period):
        return False

    if num_of_object and sum(pattern) / period != num_of_object:
        return False

    landing = [False] * period  # Tracks where throws land

    for index, throw in enumerate(pattern):
        position = (throw + index) % period
        if landing[position]:  # Collision detected
            return False
        landing[position] = True
    return True


def calculate_num_balls(pattern: list[int]) -> int | None:
    """
    Calculate the number of balls in the given siteswap pattern.

    The number of balls is determined by dividing the sum of the throws by the number of beats (throws in the pattern).

    Args:
        pattern (list[int]): A list representing the throws in a siteswap pattern.

    Returns:
        int: The number of balls in the pattern.
    """
    return sum(pattern) // len(pattern) if len(pattern) > 0 else None


def compute_initial_state_of_pattern(pattern: list[int]) -> list[str]:
    """
    Initialize the juggling state array based on the number of balls and throws in the pattern.

    Args:
        pattern (list[int]): A list representing the throws in a siteswap pattern.

    Returns:
        list[str]: The initial state of the juggling pattern, with "x" representing ball positions and "_" representing empty positions.
    """
    num_balls = calculate_num_balls(pattern)
    assert num_balls is not None
    state_size = max(pattern) + 1
    state = ["_"] * state_size

    # Fill first `num_balls` positions with 'x'
    for i in range(num_balls):
        state[i] = "x"

    return state


def shift_left(state: list[str]) -> list[str]:
    return state[1:] + ["_"]


def shift_state(state: list[str], throw: int) -> list[str]:
    """
    Shift the juggling state to the next step based on the current throw.

    The state is shifted left, and a ball is thrown to the position indicated by the throw value.

    Args:
        state (list[str]): The current state of the juggling pattern.
        throw (int): The throw value indicating where the ball lands.

    Returns:
        list[str]: The new state after applying the shift.

    Raises:
        ValueError: If there is a ball collision (i.e., trying to throw a ball to an already occupied position).
    """
    new_state = shift_left(state)  # Left shift: Remove leftmost, append '_'

    if state[0] == "x":  # If an 'x' was removed, we must throw
        if throw == 0:
            raise ExcitedSiteswapError(
                f"The siteswap pattern is excited: the next state cann't be calculated for throw {throw}."
            )
        if new_state[throw - 1] == "_":
            new_state[throw - 1] = "x"  # Place the landing ball
        else:
            raise ExcitedSiteswapError(
                f"The siteswap pattern is excited: the next state cann't be calculated for throw {throw}."
            )

    return new_state


def calculate_pattern_orbit(pattern: list[int]) -> list[tuple[int]]:
    assert is_valid(pattern)
    indices = set()
    res = []
    for i, throw in enumerate(pattern):
        if i in indices:
            continue
        next_index = (i + throw) % len(pattern)
        curr_orbit_indices = [i]
        while next_index != i:
            indices.add(next_index)
            curr_orbit_indices.append(next_index)
            next_index = (next_index + pattern[next_index]) % len(pattern)
        res.append(
            tuple(
                pattern[j] if j in curr_orbit_indices else 0
                for j in range(len(pattern))
            )
        )
    return res


def find_all_states(pattern: list[int]) -> set[tuple[str]]:
    entry = find_excited_entry(pattern) if is_excited_pattern(pattern) else []
    initial_state = compute_initial_state_of_pattern(pattern)
    states = set()
    for throw in entry:
        initial_state = shift_state(initial_state, throw)
    states.add(tuple(initial_state))
    for throw in pattern:
        initial_state = shift_state(initial_state, throw)
        states.add(tuple(initial_state))

    return states


def find_transition_of_certain_length(
    state1: list[str], state2: list[str], transitions_length: int
) -> list[int] | None:
    result = []
    if transitions_length == 0 and state1 == state2:
        return []
    for _ in range(transitions_length):
        state1 = shift_left(state1)
    if not all(b == "x" for a, b in zip(state1, state2) if a == "x"):
        return None

    extra_count = sum(a != "x" and b == "x" for (a, b) in zip(state1, state2))
    for i, (a, b) in enumerate(zip(state1, state2)):
        if a != "x" and b == "x":
            result.append(i + extra_count)
            extra_count -= 1
    return result if result else None


def find_minimal_transition_between_two_states(
    state1: tuple[str], state2: tuple[str]
) -> list[int] | None:
    src_state = list(state1)
    dest_state = list(state2)
    res = []
    for i in range(len(state1)):
        res = find_transition_of_certain_length(src_state, dest_state, i)
        if res is not None:
            break
    return res


def find_transition(patternA: list[int], patternB: list[int]) -> list[int] | None:
    """
    Determine the throws needed to safely transition from one pattern to another.

    Args:
        patternA (list[int]): The pattern you're currently juggling.
        patternB (list[int]): The pattern you want to transition into.

    Returns:
        list[int]: A list of throws to insert between them (transition throws).
    """
    num_balls = calculate_num_balls(patternA)
    assert num_balls is not None
    assert num_balls == calculate_num_balls(
        patternB
    ), "Patterns must have same ball count"

    A_states = find_all_states(patternA)
    B_states = find_all_states(patternB)

    minimal_transition = [0] * (num_balls + 1)
    res = []
    for stateA in A_states:
        for stateB in B_states:
            res = find_minimal_transition_between_two_states(stateA, stateB)
            if res and len(res) < len(minimal_transition):
                minimal_transition = res
    return minimal_transition


def find_excited_entry(pattern: list[int]) -> list[int]:
    """
    Determine the necessary starting throws for an excited siteswap to avoid collisions.

    Args:
        pattern (list[int]): The siteswap pattern to analyze.

    Returns:
        list[int]: A list of necessary starting throws.
    """
    num_balls = calculate_num_balls(pattern)
    assert num_balls is not None
    max_throw = max(pattern)
    base_entry_length = num_balls

    entry = [num_balls] * base_entry_length

    landing_pos = set(
        pattern[i % len(pattern)] + i + base_entry_length for i in range(num_balls)
    )
    full_pattern = (
        entry
        + [pattern[i % len(pattern)] for i in range(num_balls)]
        + [False] * max_throw
    )
    for pos in landing_pos:
        full_pattern[pos] = True

    first_change_index = None
    for i, entry_throw in enumerate(entry):
        if full_pattern[i + entry_throw] is True:
            if first_change_index is None:
                first_change_index = i
            first_free_pos = full_pattern.index(False)
            full_pattern[i] = first_free_pos - i
            full_pattern[first_free_pos] = True

    return full_pattern[first_change_index:base_entry_length]


def is_excited_pattern(pattern: list[int]) -> bool:
    num_balls = calculate_num_balls(pattern)
    assert num_balls is not None
    for i, throw in enumerate(pattern):
        if throw + i < num_balls:
            return True
    return False


def is_prime_siteswap(pattern: list[int]) -> bool | None:
    """
    Check if a given siteswap pattern is prime.

    A prime siteswap cannot be decomposed into smaller patterns. This function checks for repeated states
    during the juggling process to determine if the pattern is prime or composite.

    Args:
        pattern (list[int]): A list representing the throws in a siteswap pattern.

    Returns:
        bool: `True` if the pattern is prime, `False` if it is composite.
    """
    if not is_valid(pattern):
        raise NotValidSiteswapError
    state = compute_initial_state_of_pattern(pattern)
    assert state is not None
    seen_states = set()

    for throw in pattern:
        state_tuple = tuple(state)
        if state_tuple in seen_states:
            return False  # Repeated state before completing cycle => Composite

        seen_states.add(state_tuple)
        state = shift_state(state, throw)

    return True  # No repeated state before completing full cycle => Prime


def decompose_siteswap_recursive(
    pattern: list[int],
    current_state: list[str],
    res: list[tuple[int, ...]],
    is_seen: bool = False,
    seen_states: dict[tuple[str, ...], int] | None = None,
    pattern_prefix_pre_cycle: list[int] | None = None,
) -> None:
    """
    Recursively decompose a siteswap pattern into smaller subpatterns.

    The function looks for repeating states during the juggling process, which indicate where the pattern
    can be split into smaller cycles.

    Args:
        pattern (list[int]): A list representing the throws in a siteswap pattern.
        res (list[tuple[int]]): The list to accumulate the decomposed subpatterns.
    """
    if seen_states is None:
        seen_states = {}
    if pattern_prefix_pre_cycle is None:
        pattern_prefix_pre_cycle = []

    for local_index, throw in enumerate(pattern):
        current_state = shift_state(current_state, throw)
        state_tuple = tuple(current_state)
        if state_tuple in seen_states:
            seen_states = {state_tuple: seen_states[state_tuple]}
            start_index = seen_states[state_tuple] + 1 if not is_seen else 0
            res.append(tuple(pattern[start_index : local_index + 1]))
            if not pattern_prefix_pre_cycle:
                pattern_prefix_pre_cycle = pattern[:start_index]
            decompose_siteswap_recursive(
                pattern[local_index + 1 :],
                current_state,
                res,
                True,
                seen_states,
                pattern_prefix_pre_cycle,
            )
            return
        if not is_seen:
            seen_states[state_tuple] = local_index

    res.append(
        tuple(pattern + pattern_prefix_pre_cycle)
    )  # If no repeats, add the rest of the pattern


def decompose_siteswap(
    pattern: list[int],
    entry: list[int] | None = None,
) -> list[str]:
    """
    Decompose a siteswap pattern into its repeating subpatterns and their counts.

    This function first recursively decomposes the pattern and then counts the number of occurrences
    of each subpattern. The result is formatted to display the count of each subpattern.

    Args:
        pattern (list[int]): A list representing the throws in a siteswap pattern.

    Returns:
        list[str]: A list of strings representing the decomposed patterns with their counts.
    """
    state = compute_initial_state_of_pattern(pattern)
    assert state is not None
    if entry:
        for throw in entry:
            state = shift_state(state, throw)

    res = []
    decompose_siteswap_recursive(pattern, state, res)

    # Count repetitions of patterns
    counter = Counter(res)

    # Format the results
    formatted_result = []
    for pattern, count in counter.items():
        if len(pattern) == 1:
            formatted_result.append(
                "(" + str(pattern[0]) + ")" + f"^{count}"
                if count > 1
                else "(" + str(pattern[0]) + ")"
            )  # For single elements, repeat as string
        else:
            formatted_result.append(
                f"({' '.join(map(str, pattern))})^{count}"
            )  # Decomposed patterns with count

    formatted_result.sort(
        reverse=True,
        key=lambda x: (
            int(x.split("^")[1]) if "^" in x else 1,  # Extract power for sorting
            len(x.split(" ")[0].split(",")),  # Period (length of pattern)
            int(
                x.split(" ")[0].split("(")[1]
                if " " in x
                else x.split("(")[1].split(")")[0]
            ),  # First number in the period
        ),
    )

    return formatted_result


# print(is_prime_siteswap([4, 2, 3]))
# print(is_prime_siteswap([7, 7, 7, 9, 7, 5, 0]))
# print(is_prime_siteswap([4, 8, 0, 0, 1, 2, 0, 1]))
# print(is_prime_siteswap([8, 4, 9, 6, 2, 2, 4]))

# print(decompose_siteswap([4, 2, 3, 3, 3]))
# print(decompose_siteswap([5, 3, 1]))
# print(decompose_siteswap([3, 5, 3, 1, 4, 2, 3, 5, 3, 1]))
# print(is_valid([ 4, 4, 5, 0, 4, 4, 0, 3, 4, 4, 1, 3, 3, 4, 2]))
# print(decompose_siteswap([ 4, 4, 5, 0, 4, 4, 0, 3, 4, 4, 1, 3, 3, 4, 2]))

# print(decompose_siteswap([9, 4, 5, 8, 4], [7]))

# print(find_excited_entry([7,8,8,9,0,1,2]))
# print(decompose_siteswap([7,8,9,5,6]))
# print(find_excited_entry([7,1,4]))
# print(is_excited_pattern([7,7,1]))
# num_of_siteswaps = 0
# last_num = 0
# for i in range(20000000):
#     l = [int(digit) for digit in str(i)]
#     if is_valid(l):
#         num_of_siteswaps += 1
#     if i % 1000000 == 0:
#         print(i, num_of_siteswaps, num_of_siteswaps - last_num)
#         last_num = num_of_siteswaps

# a = find_transition([5, 3, 1], [4, 4, 1])
# print(a)
# print(find_excited_entry([11,6,1]))

# print(decompose_siteswap([8, 9, 5, 6]))

# print(decompose_siteswap([8, 9, 5,9,5,9,5, 6]))
# print(decompose_siteswap([7,8, 9, 5,9,5,9,5, 6,8,9,5,9,5,6]))
#
# print(decompose_siteswap([7,8,9,5,6,7,8,9,5,9,5,6]))
# print(calculate_pattern_orbit([9,9,6,8,9,7,8]))
# print(find_transition_of_certain_length(['x', 'x', 'x', '_', 'x', '_', '_', '_'], ['x', 'x', '_', 'x', 'x', '_', '_', '_'], 1))
# print(find_excited_entry([7,4,1]))
# print(find_transition_of_certain_length(['x', 'x', '_', 'x', 'x', '_', '_', '_'], ['x', 'x', 'x', '_', 'x', '_', '_', '_'], 2))

# state = compute_initial_state_of_pattern([7,4,1])
# for throw in [5]:
#     state = shift_state(state, throw)
# print(state)
print(find_transition([7, 4, 1], [7, 1, 4]))
