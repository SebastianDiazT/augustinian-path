
from apps.schedules.generator import (
    _occupied_blocks_by_day,
    bitmask_from_meetings,
    build_course_options,
    describe_combination,
    find_incompatible_pair,
    resolve_conflicts_and_branch,
    score_combination,
    search_valid_combinations,
)


def test_bitmask_utilities():
    meetings = [('monday', 1), ('friday', 2)]
    mask = bitmask_from_meetings(meetings)
    assert mask == (1 << 0) | (1 << 65)

    occupied = _occupied_blocks_by_day(mask)
    assert occupied[0] == [0]
    assert occupied[4] == [1]
    assert occupied[1] == []


def test_build_course_options_no_lab():
    opts = build_course_options(1, 'Curso', [(10, 'i1', 3)], [])
    assert len(opts.options) == 1
    assert opts.options[0].section_ids == (10,)


def test_build_course_options_with_lab():
    opts = build_course_options(1, 'Curso', [(10, 'i1', 1)], [(20, 'i2', 2), (21, 'i3', 1)])
    assert len(opts.options) == 1
    assert opts.options[0].bitmask == 3
    assert opts.options[0].section_ids == (10, 20)


def test_search_and_score_combinations():
    opt1 = build_course_options(1, 'A', [(10, 'i1', 1)], [])
    opt2 = build_course_options(2, 'B', [(20, 'i2', 2)], [])
    opt3 = build_course_options(3, 'C', [(30, 'i3', 1)], [])

    combos = search_valid_combinations([opt1, opt2])
    assert len(combos) == 1

    pair = find_incompatible_pair([opt1, opt3])
    assert pair == (1, 3)

    prefs = {'maximize_free_days': True, 'preferred_instructor_ids': ['i1']}
    score = score_combination(combos[0], prefs)
    assert score > 0


def test_branching_logic():
    opt1 = build_course_options(1, 'A', [(10, 'i1', 1)], [])
    opt2 = build_course_options(2, 'B', [(20, 'i2', 1)], [])

    branches = resolve_conflicts_and_branch([opt1, opt2], lambda a, b: None)
    assert len(branches) == 2

    assert branches[0][0][0].offering_id == 1
    assert branches[1][0][0].offering_id == 2


def test_describe_combination():
    opt = build_course_options(1, 'A', [(10, 'i1', bitmask_from_meetings([('monday', 1)]))], [])
    combo = {1: opt.options[0]}
    desc = describe_combination(combo, {})
    assert 'Libre los' in desc or 'Libre el' in desc
