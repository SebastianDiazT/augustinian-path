"""Pure schedule-generation algorithm: backtracking search with bitmask
pruning. No database access here on purpose — see services.py for the
part that loads data and persists results. Keeping this pure makes the
algorithm itself cheap to unit test with plain Python objects, no DB
required.

Latency strategy (see project notes for the full reasoning):
  - Every weekly time slot (day x 50-minute block) maps to one bit in a
    single Python int. Checking whether two schedules clash is one
    bitwise AND — O(1), not a comparison of sets or time ranges.
  - Courses are searched in order of fewest options first (the
    "most-constrained-variable" heuristic), so bad branches get pruned
    as early as possible instead of being discovered deep in the tree.
  - Hard caps on both the number of complete solutions collected and
    the number of backtracking steps explored guarantee this terminates
    quickly even on pathological inputs — it degrades gracefully
    (returns whatever it found) instead of hanging a request.
  - A cheap pairwise pre-check (find_incompatible_pair) detects "these
    two specific courses can never coexist" before the main search even
    starts, which is both a latency win and what powers the "curso
    crítico" tie-break and the diagnostic message when nothing is
    found.
"""

from dataclasses import dataclass, field

BLOCKS_PER_DAY = 16
DAY_INDEX = {
    'monday': 0, 'tuesday': 1, 'wednesday': 2,
    'thursday': 3, 'friday': 4, 'saturday': 5,
}
DAY_LABELS_ES = {
    0: 'lunes', 1: 'martes', 2: 'miércoles',
    3: 'jueves', 4: 'viernes', 5: 'sábado',
}

DEFAULT_MAX_SOLUTIONS = 200
DEFAULT_MAX_STEPS = 200_000

DEFAULT_SCORE_WEIGHTS = {
    'preferred_free_day': 10,
    'maximize_free_days': 3,
    'time_of_day_violation': -5,
    'gap_block': -2,
    'preferred_instructor': 4,
}


def meeting_bit(day_of_week: str, block_order: int) -> int:
    return DAY_INDEX[day_of_week] * BLOCKS_PER_DAY + (block_order - 1)


def bitmask_from_meetings(meetings) -> int:
    """meetings: iterable of (day_of_week, block_order) tuples."""

    mask = 0
    for day_of_week, block_order in meetings:
        mask |= 1 << meeting_bit(day_of_week, block_order)
    return mask


def _occupied_blocks_by_day(bitmask: int) -> dict:
    by_day = {d: [] for d in range(6)}
    bit = 0
    remaining = bitmask
    while remaining:
        if remaining & 1:
            by_day[bit // BLOCKS_PER_DAY].append(bit % BLOCKS_PER_DAY)
        remaining >>= 1
        bit += 1
    return by_day


@dataclass(frozen=True)
class CourseOption:
    """One selectable way to take a course: a theory section alone, or a
    (theory, lab) pair whose own meetings don't clash with each other."""

    offering_id: int
    section_ids: tuple
    instructor_ids: tuple
    bitmask: int


@dataclass
class CourseOptions:
    offering_id: int
    course_name: str
    options: list = field(default_factory=list)


def build_course_options(offering_id, course_name, theory_sections, lab_sections):
    """theory_sections / lab_sections: list of (section_id, instructor_id,
    bitmask) tuples, already filtered for exclusions. If lab_sections is
    empty, the course has no lab and each theory section is its own
    option."""

    options = []
    if not lab_sections:
        for theory_id, theory_instructor_id, theory_mask in theory_sections:
            options.append(
                CourseOption(offering_id, (theory_id,), (theory_instructor_id,), theory_mask),
            )
        return CourseOptions(offering_id, course_name, options)

    for theory_id, theory_instructor_id, theory_mask in theory_sections:
        for lab_id, lab_instructor_id, lab_mask in lab_sections:
            if theory_mask & lab_mask == 0:
                options.append(
                    CourseOption(
                        offering_id,
                        (theory_id, lab_id),
                        (theory_instructor_id, lab_instructor_id),
                        theory_mask | lab_mask,
                    ),
                )
    return CourseOptions(offering_id, course_name, options)


def find_incompatible_pair(course_options_list):
    """Returns (offering_id_a, offering_id_b) for the first pair of
    courses with ZERO conflict-free combination between just the two of
    them — or None if every pair has at least one way to coexist. Cheap:
    option counts per course are typically single digits."""

    for i in range(len(course_options_list)):
        for j in range(i + 1, len(course_options_list)):
            a = course_options_list[i]
            b = course_options_list[j]
            if not any(
                opt_a.bitmask & opt_b.bitmask == 0
                for opt_a in a.options
                for opt_b in b.options
            ):
                return a.offering_id, b.offering_id
    return None


def resolve_conflicts_and_branch(course_options_list, pick_course_to_drop_fn):
    """Repeatedly finds pairwise-incompatible courses and asks
    `pick_course_to_drop_fn(offering_id_a, offering_id_b)` what to do
    about it — it must return either (dropped_offering_id, reason) to
    keep a single variant going, or None when neither course should be
    preferred, which branches this into two variants (one dropping
    each). Terminates naturally: every step removes one course from at
    least one branch, so with N courses there are at most N-1 rounds.

    Returns a list of (course_options_list, notes) — normally just one,
    two only when an unresolvable tie was hit."""

    pending = [(list(course_options_list), [])]
    resolved = []

    while pending:
        current, notes = pending.pop()
        pair = find_incompatible_pair(current)
        if pair is None:
            resolved.append((current, notes))
            continue

        offering_id_a, offering_id_b = pair
        decision = pick_course_to_drop_fn(offering_id_a, offering_id_b)

        if decision is not None:
            dropped_id, reason = decision
            remaining = [c for c in current if c.offering_id != dropped_id]
            pending.append((remaining, notes + [reason]))
        else:
            by_id = {c.offering_id: c for c in current}
            name_a = by_id[offering_id_a].course_name
            name_b = by_id[offering_id_b].course_name
            base_reason = (
                f'"{name_a}" y "{name_b}" se cruzan por completo en todos sus '
                'grupos y no fue posible priorizar uno automáticamente, así '
                'que se generó una alternativa excluyendo a cada uno.'
            )
            without_a = [c for c in current if c.offering_id != offering_id_a]
            without_b = [c for c in current if c.offering_id != offering_id_b]
            pending.append((without_a, notes + [f'Se excluyó "{name_a}". {base_reason}']))
            pending.append((without_b, notes + [f'Se excluyó "{name_b}". {base_reason}']))

    return resolved


def search_valid_combinations(
    course_options_list,
    max_solutions=DEFAULT_MAX_SOLUTIONS,
    max_steps=DEFAULT_MAX_STEPS,
):
    """Backtracking search with bitmask pruning, courses ordered by
    fewest options first. Returns a list of complete combinations, each
    a dict {offering_id: CourseOption}, capped at `max_solutions`. Stops
    exploring (returns whatever it found so far) once `max_steps`
    backtracking steps have been taken."""

    if not course_options_list:
        return []

    ordered = sorted(course_options_list, key=lambda c: len(c.options))
    solutions = []
    steps = [0]

    def backtrack(index, chosen, used_mask):
        if len(solutions) >= max_solutions or steps[0] >= max_steps:
            return
        if index == len(ordered):
            solutions.append(dict(chosen))
            return
        for option in ordered[index].options:
            steps[0] += 1
            if steps[0] >= max_steps:
                return
            if used_mask & option.bitmask:
                continue
            chosen[ordered[index].offering_id] = option
            backtrack(index + 1, chosen, used_mask | option.bitmask)
            del chosen[ordered[index].offering_id]
            if len(solutions) >= max_solutions:
                return

    backtrack(0, {}, 0)
    return solutions


def score_combination(combination, preferences, weights=None):
    weights = weights or DEFAULT_SCORE_WEIGHTS
    total_mask = 0
    instructor_ids = set()
    for option in combination.values():
        total_mask |= option.bitmask
        instructor_ids.update(option.instructor_ids)

    by_day = _occupied_blocks_by_day(total_mask)
    free_day_indices = {day for day, blocks in by_day.items() if not blocks}

    score = 0.0

    preferred_free_days = preferences.get('preferred_free_days') or []
    preferred_day_indices = {DAY_INDEX[d] for d in preferred_free_days if d in DAY_INDEX}
    score += len(preferred_day_indices & free_day_indices) * weights['preferred_free_day']

    if preferences.get('maximize_free_days'):
        score += len(free_day_indices) * weights['maximize_free_days']

    time_range = preferences.get('time_of_day_range')
    if time_range:
        earliest = time_range.get('earliest_block', 1)
        latest = time_range.get('latest_block', BLOCKS_PER_DAY)
        for blocks in by_day.values():
            for block in blocks:
                block_order = block + 1
                if block_order < earliest or block_order > latest:
                    score += weights['time_of_day_violation']

    if preferences.get('minimize_gaps'):
        for blocks in by_day.values():
            if len(blocks) > 1:
                gaps = (blocks[-1] - blocks[0] + 1) - len(blocks)
                score += gaps * weights['gap_block']

    preferred_instructors = set(preferences.get('preferred_instructor_ids') or [])
    score += len(instructor_ids & preferred_instructors) * weights['preferred_instructor']

    return score


def describe_combination(combination, preferences):
    """Short, human-readable summary in Spanish (user-facing text)."""

    total_mask = 0
    for option in combination.values():
        total_mask |= option.bitmask
    by_day = _occupied_blocks_by_day(total_mask)
    free_days = [DAY_LABELS_ES[d] for d, blocks in by_day.items() if not blocks]

    parts = []
    if free_days:
        label = 'Libre los' if len(free_days) > 1 else 'Libre el'
        parts.append(f'{label} {", ".join(free_days)}')

    occupied_days = [d for d, blocks in by_day.items() if blocks]
    if occupied_days:
        earliest_block = min(min(blocks) for blocks in by_day.values() if blocks)
        latest_block = max(max(blocks) for blocks in by_day.values() if blocks)
        if latest_block <= 8:  # roughly midday, block 9 starts the afternoon
            parts.append('clases solo en la mañana')
        elif earliest_block >= 8:
            parts.append('sin clases en la mañana')

    return ', '.join(parts).capitalize() if parts else 'Horario compacto'


def top_alternatives(course_options_list, preferences, n=4, max_solutions=DEFAULT_MAX_SOLUTIONS, max_steps=DEFAULT_MAX_STEPS):
    """Returns up to `n` (combination, score, description) tuples, best
    first. `max_solutions` already keeps the candidate pool small
    (≤200), so a plain sort here is simpler than a streaming heap and
    costs nothing measurable."""

    combinations = search_valid_combinations(course_options_list, max_solutions, max_steps)
    scored = [
        (combo, score_combination(combo, preferences), describe_combination(combo, preferences))
        for combo in combinations
    ]
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:n]
