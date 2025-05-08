def generate_siteswaps(
    period_length: int,
    num_of_objects: int,
    juggler_A_pattern: [int],
    min_throw: int = 2,
    max_throw: int = 14,
):
    assert len(juggler_A_pattern) * 2 == period_length
    assert period_length > 0 and period_length / 2 == int(period_length / 2)
    assert num_of_objects > 0
    assert len(juggler_A_pattern) < period_length
    assert [
        min_throw < juggler_A_pattern[i] < max_throw
        for i in range(len(juggler_A_pattern))
    ] == [True for i in range(len(juggler_A_pattern))]

    valid_patterns = []
    pattern = [None] * period_length
    for i in range(int(period_length / 2)):
        pattern[i * 2] = juggler_A_pattern[i]

    fill_pattern(pattern, 1, valid_patterns, num_of_objects)
    return valid_patterns


def fill_pattern(
    pattern: [int],
    index: int,
    valid_patterns,
    num_of_obj: int,
    min_throw: int = 2,
    max_throw: int = 14,
):  # recursive
    temp_pattern = pattern[:]
    for throw in range(min_throw, max_throw + 1):
        temp_pattern[index] = throw

        if None in temp_pattern:
            fill_pattern(
                temp_pattern,
                index + 2,
                valid_patterns,
                num_of_obj,
                min_throw,
                max_throw,
            )
        else:
            if is_valid(temp_pattern, num_of_obj):
                final_pattern = temp_pattern[:]
                valid_patterns.append(final_pattern)
                print(temp_pattern)


def is_valid(pattern: [int], num_of_obj: int):
    period = len(pattern)
    landing = [False] * period
    valid = True
    for index, throw in enumerate(pattern):
        position = (throw + index) % period
        if landing[position] is True:
            valid = False
        landing[position] = True
    if not (sum(pattern) / period) == num_of_obj:
        valid = False
    return valid


if __name__ == "__main__":
    print(generate_siteswaps(10, 7, [8, 7, 6, 5, 4]))
