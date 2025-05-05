from itertools import product

from tools import is_valid


def count_valid_siteswaps(period):
    """
    Count the number of valid siteswaps for a given period.
    """
    valid_count = 0

    # Generate all possible patterns of length `period` with digits 0-9
    for digits in product(range(10), repeat=period):
        if is_valid(digits):
            # print(digits)
            valid_count += 1

    return valid_count


# Simulate for period 4
period = 8
valid_siteswaps_period_4 = count_valid_siteswaps(period)
print(valid_siteswaps_period_4)
print(valid_siteswaps_period_4 / pow(10, period))


# period = 7
# throw = 9

# res = 0
# for ball in range(1, 10):
#     for i in range(period + 1):
#         if period + ball - 1 - i *(throw + 1) >= 0:
#             res += pow(-1, i) * math.comb(period, i) * math.comb(period + ball - 1 - i *(throw + 1), period - 1)

# print(res)
