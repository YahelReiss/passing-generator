from collections import deque
from typing import Dict, Tuple

def build_graph(num_balls: int, max_throw: int) -> Dict:
    def shift_and_throw(state: Tuple[int], throw: int) -> Tuple[int]:
        new_state = state[1:] + ("-",)
        if throw == 0:
            return tuple(new_state)
        if throw < len(new_state) + 1:
            new_state = list(new_state)
            new_state[throw - 1] = "x"
            return tuple(new_state)
        return None  # invalid throw

    if num_balls > max_throw:
        return {}

    ground_state = tuple(["x"] * num_balls + ["-"] * (max_throw - num_balls))
    visited = {}
    queue = deque([ground_state])
    id_counter = 0

    nodes = []
    edges = []
    while queue:
        state = queue.popleft()
        if state not in visited:
            visited[state] = id_counter
            nodes.append({"id": "".join(state)})
            id_counter += 1

        source_id = visited[state]
        if state[0] == "x":
            valid_throws = [t for t in range(max_throw + 1) if (t == max_throw) or state[t] == "-"]
        else:
            valid_throws = [0]  # no ball in hand — must "wait"

        for throw in valid_throws:
            next_state = shift_and_throw(state, throw)
            if next_state is None:
                continue

            if next_state not in visited:
                visited[next_state] = id_counter
                nodes.append({"id": "".join(next_state)})
                id_counter += 1
                queue.append(next_state)

            edges.append({
                "source": "".join(state),
                "target": "".join(next_state),
                "label": str(throw)
            })

    return {"nodes": nodes, "edges": edges}
