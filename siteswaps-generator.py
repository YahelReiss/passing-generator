import argparse
from collections import Counter
from typing import List, Optional, Union

from colorama import Fore, Style

from tools import is_valid


def generate_siteswaps(
    period_length: int,
    num_of_objects: int,
    partial_pattern: List[Union[int, str]],
    min_throw: int = 2,
    max_throw: int = 14,
    exclude_throws: Optional[List[int]] = [1, 3],
    include_throws: Optional[List[int]] = None,
) -> List[List[int]]:
    """
    Generate siteswap patterns by completing a given partial pattern.

    Args:
        period_length: Total length of the pattern.
        num_of_objects: Number of objects in the pattern.
        partial_pattern: A list representing the partial pattern (e.g., [None, None, 4, None, 6, None]).
        min_throw: Minimum value for a throw.
        max_throw: Maximum value for a throw.
        exclude_throws: A list of throws to exclude from the patterns.
        include_throws: A list of throws that must appear at least once in every pattern.

    Returns:
        A list of valid completed siteswap patterns.
    """
    # Validate inputs
    if period_length <= 0:
        raise ValueError("Period length must be a positive even number.")
    if num_of_objects <= 0:
        raise ValueError("Number of objects must be positive.")
    if len(partial_pattern) != period_length:
        raise ValueError("Partial pattern length must match the period length.")
    if exclude_throws and include_throws and set(exclude_throws) & set(include_throws):
        raise ValueError("A throw cannot be both excluded and included.")
    if not all(
        (throw is None or (min_throw <= throw <= max_throw))
        for throw in partial_pattern
    ):
        raise ValueError(
            f"Throws in the partial pattern must be between {min_throw} and {max_throw}, or None."
        )

    # Prepare the pattern by replacing placeholders with None
    pattern = [None if throw in (None, "_") else throw for throw in partial_pattern]

    generator_indices = [i for i, throw in enumerate(pattern) if throw is None]

    exclude_throws = set(exclude_throws or [])
    include_throws = set(include_throws or [])
    valid_patterns = []
    fill_pattern(
        pattern,
        0,
        valid_patterns,
        num_of_objects,
        min_throw,
        max_throw,
        exclude_throws,
        include_throws,
        generator_indices,
    )
    return deduplicate_patterns(valid_patterns)


def deduplicate_patterns(patterns: List[List[int]]) -> List[List[int]]:
    """
    Remove duplicate patterns by considering rotations as identical and keeping the canonical rotation.

    Args:
        patterns: A list of generated siteswap patterns.

    Returns:
        A deduplicated list of patterns.
    """
    unique_patterns = set()
    canonical_patterns = []

    for pattern in patterns:
        rotations = [pattern[i:] + pattern[:i] for i in range(len(pattern))]
        canonical_rotation = max(
            rotations
        )  # Keep the rotation that starts with the largest number
        if tuple(canonical_rotation) not in unique_patterns:
            unique_patterns.add(tuple(canonical_rotation))
            canonical_patterns.append(canonical_rotation)

    return canonical_patterns


def fill_pattern(
    pattern: List[Optional[int]],
    index: int,
    valid_patterns: List[List[int]],
    num_of_objects: int,
    min_throw: int,
    max_throw: int,
    exclude_throws: set,
    include_throws: set,
    generator_indices: List[int],
) -> None:
    """
    Recursive function to generate all valid siteswap patterns by filling in the missing throws.

    Args:
        pattern: The current state of the pattern being generated.
        index: The current index being processed.
        valid_patterns: A list to collect valid patterns.
        num_of_objects: The number of objects to balance in the pattern.
        min_throw: Minimum throw value.
        max_throw: Maximum throw value.
        exclude_throws: A set of throws to exclude from the patterns.
        include_throws: A set of throws that must appear at least once in every pattern.
        generator_indices: Indices in the pattern that are filled by the generator.
    """
    if index >= len(pattern):  # Reached the end of the pattern
        filled_values = {pattern[i] for i in generator_indices}
        if (
            is_valid(pattern, num_of_objects)
            and include_throws.issubset(filled_values)
            and len(Counter(pattern)) > 1
        ):
            valid_patterns.append(pattern[:])  # Add a copy of the valid pattern
        return

    if pattern[index] is not None:  # Skip prefilled throws
        fill_pattern(
            pattern,
            index + 1,
            valid_patterns,
            num_of_objects,
            min_throw,
            max_throw,
            exclude_throws,
            include_throws,
            generator_indices,
        )
    else:
        for throw in range(min_throw, max_throw + 1):  # Try all possible throws
            if throw in exclude_throws:
                continue  # Skip excluded throws
            pattern[index] = throw
            fill_pattern(
                pattern,
                index + 1,
                valid_patterns,
                num_of_objects,
                min_throw,
                max_throw,
                exclude_throws,
                include_throws,
                generator_indices,
            )
            pattern[index] = None


def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate valid siteswap patterns.")

    # Add arguments
    parser.add_argument(
        "--period_length",
        type=int,
        required=True,
        help="Length of the siteswap period.",
    )
    parser.add_argument(
        "--num_objects",
        type=int,
        required=True,
        help="Number of objects in the siteswap.",
    )
    parser.add_argument("--min_throw", type=int, default=2, help="Minimum throw value.")
    parser.add_argument(
        "--max_throw", type=int, default=14, help="Maximum throw value."
    )
    parser.add_argument(
        "--exclude_throws",
        type=int,
        nargs="*",
        default=[1, 3],
        help="Throws to exclude.",
    )
    parser.add_argument(
        "--include_throws",
        type=int,
        nargs="*",
        default=None,
        help="Throws that must appear at least once.",
    )
    parser.add_argument(
        "--partial_pattern",
        type=int,
        nargs="*",
        default=None,
        help="Partial pattern (use None for placeholders).",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    partial_pattern = (
        [None if x == -1 else x for x in args.partial_pattern]
        if args.partial_pattern
        else [None] * args.period_length
    )

    result = generate_siteswaps(
        period_length=args.period_length,
        num_of_objects=args.num_objects,
        partial_pattern=partial_pattern,
        min_throw=args.min_throw,
        max_throw=args.max_throw,
        exclude_throws=args.exclude_throws,
        include_throws=args.include_throws,
    )

    print("Generated Patterns:")
    if not result:
        print("no siteswaps found")
    else:
        print(f"{len(result)} siteswaps were found")
        for pattern in result:
            for index, element in enumerate(pattern):
                # Alternate colors based on index
                if index % 2 == 0:
                    print(Fore.RED + str(element), end=" ")  # Even index in red
                else:
                    print(Fore.GREEN + str(element), end=" ")  # Odd index in green
            print()
        print(Style.RESET_ALL)  # Reset color after each pattern


# Example usage
if __name__ == "__main__":
    exit(main())
