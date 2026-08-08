"""Independent exact SageMath checks for the computable carrier frontier."""

from itertools import combinations, product

K.<omega> = CyclotomicField(3)
R.<a,b,c> = PolynomialRing(K)


def unsigned_maximal_minors(matrix):
    """Return determinants after deleting one row."""

    rows = matrix.nrows()
    columns = matrix.ncols()
    return tuple(
        matrix.matrix_from_rows(
            tuple(row for row in range(rows) if row != removed)
        ).det()
        for removed in range(rows)
        if rows == columns + 1
    )


def column_maximal_minors(matrix):
    """Return all maximal minors selected by columns."""

    return tuple(
        matrix.matrix_from_columns(columns).det()
        for columns in combinations(range(matrix.ncols()), matrix.nrows())
    )


def transform_matrix(matrix, images):
    """Apply one simultaneous coordinate substitution entrywise."""

    return matrix.apply_map(lambda entry: entry(*images))


def relation_matrix(hilbert_burch, extension):
    """Push out a four-by-three Hilbert--Burch matrix by one class."""

    return hilbert_burch.transpose().augment(
        matrix(R, hilbert_burch.ncols(), 1, tuple(-entry for entry in extension))
    )


def middle_action(target_action, character):
    """Extend the dual ideal-generator action by one class character."""

    result = zero_matrix(R, 5, 5)
    dual = target_action.transpose()
    for row in range(4):
        for column in range(4):
            result[row, column] = dual[row, column]
    result[4, 4] = character
    return result


def assert_hilbert_burch(hilbert_burch, generators):
    """Check syzygies, maximal minors, and projective length nine."""

    assert matrix(R, 1, 4, generators) * hilbert_burch == zero_matrix(R, 1, 3)
    assert R.ideal(unsigned_maximal_minors(hilbert_burch)) == R.ideal(generators)
    assert R.ideal(generators).hilbert_polynomial() == 9


def assert_fitting_cover(relation):
    """Check that maximal minors generate one on every projective chart."""

    minors = column_maximal_minors(relation)
    assert len(minors) == 10
    assert all(minor != 0 for minor in minors)
    for pivot in (a, b, c):
        affine_minors = tuple(minor.subs({pivot: 1}) for minor in minors)
        assert R.ideal(affine_minors).is_one()


def assert_chern_data():
    """Derive exact rank and Chern coefficients from the graded shifts."""

    source_shifts = (5, 5, 5)
    target_shifts = (3, 4, 4, 4, 3)
    rank = len(target_shifts) - len(source_shifts)
    first_chern = sum(source_shifts) - sum(target_shifts)
    ch_two = (
        sum(shift^2 for shift in target_shifts)
        - sum(shift^2 for shift in source_shifts)
    ) / 2
    second_chern = first_chern^2 / 2 - ch_two
    assert (rank, first_chern, second_chern) == (2, -3, 9)
    assert first_chern % 3 == 0


P_IMAGES = (omega*b, omega^2*c, a)
T_IMAGES = (a, omega*b, omega^2*c)
CENTRAL_IMAGES = (omega*a, omega*b, omega*c)
P_COORDINATES = matrix(R, ((0, omega, 0), (0, 0, omega^2), (1, 0, 0)))
T_COORDINATES = diagonal_matrix(R, (1, omega, omega^2))
SOURCE_CENTRAL = diagonal_matrix(R, (omega^2, omega^2, omega^2))
TARGET_CENTRAL = diagonal_matrix(R, (1, omega, omega, omega))
MIDDLE_CENTRAL = diagonal_matrix(R, (1, omega, omega, omega, 1))


HB_U = matrix(
    R,
    (
        (a^2-b*c, a*c-b^2, a*b-c^2),
        (c, -b, 0),
        (a, 0, -b),
        (0, a, c),
    ),
)
GENERATORS_U = (
    a*b*c,
    -a^3*b+a^2*c^2,
    -a*c^3+b^2*c^2,
    -a^2*b^2+b^3*c,
)
P_SOURCE_U = matrix(R, ((0, 0, -1), (-omega^2, 0, 0), (0, omega, 0)))
T_SOURCE_U = diagonal_matrix(R, (1, omega^2, omega))
P_TARGET_U = matrix(
    R,
    (
        (1, 0, 0, 0),
        (0, 0, omega, 0),
        (0, 0, 0, -1),
        (0, -omega^2, 0, 0),
    ),
)
T_TARGET_U = diagonal_matrix(R, (1, omega, 1, omega^2))


HB_V = matrix(
    R,
    (
        (a*b-c^2, a^2-b*c, -a*c+b^2),
        (-c, b, 0),
        (a, 0, -b),
        (0, a, c),
    ),
)
GENERATORS_V = (
    a*b*c,
    -a^3*c+a^2*b^2,
    -a^2*c^2+b*c^3,
    -a*b^3+b^2*c^2,
)
P_SOURCE_V = matrix(R, ((0, 0, -omega), (-1, 0, 0), (0, omega^2, 0)))
T_SOURCE_V = diagonal_matrix(R, (omega, 1, omega^2))
P_TARGET_V = matrix(
    R,
    (
        (1, 0, 0, 0),
        (0, 0, -omega^2, 0),
        (0, 0, 0, -omega),
        (0, 1, 0, 0),
    ),
)
T_TARGET_V = diagonal_matrix(R, (1, omega^2, omega, 1))


EXTENSIONS = (
    (b^2, -c^2, -a^2),
    (b^2, -omega*c^2, -omega^2*a^2),
    (b^2, -omega^2*c^2, -omega*a^2),
)


def assert_projective_cocycles(
    hilbert_burch,
    source_p,
    source_t,
    target_p,
    target_t,
    p_characters,
    t_character,
):
    """Check one honest projective sheaf action for each explicit extension."""

    assert P_COORDINATES * T_COORDINATES == omega * T_COORDINATES * P_COORDINATES
    assert source_p * source_t == SOURCE_CENTRAL.inverse() * source_t * source_p
    assert target_p * target_t == TARGET_CENTRAL.inverse() * target_t * target_p
    for extension, p_character in zip(EXTENSIONS, p_characters):
        relation = relation_matrix(hilbert_burch, extension)
        p_middle = middle_action(target_p, p_character)
        t_middle = middle_action(target_t, t_character)
        assert source_p.transpose() * relation == (
            transform_matrix(relation, P_IMAGES) * p_middle
        )
        assert source_t.transpose() * relation == (
            transform_matrix(relation, T_IMAGES) * t_middle
        )
        assert p_middle^3 == identity_matrix(R, 5)
        assert t_middle^3 == identity_matrix(R, 5)
        assert p_middle * MIDDLE_CENTRAL == MIDDLE_CENTRAL * p_middle
        assert t_middle * MIDDLE_CENTRAL == MIDDLE_CENTRAL * t_middle
        assert p_middle * t_middle == MIDDLE_CENTRAL * t_middle * p_middle
        assert transform_matrix(relation, CENTRAL_IMAGES) == (
            SOURCE_CENTRAL * relation * MIDDLE_CENTRAL.inverse()
        )
        assert_fitting_cover(relation)


F = -3*(1+omega)*a^3 + 3*b^3 + 3*omega*c^3
G = -3*(1+2*omega)*(a^3+b^3+c^3) + 18*(2+omega)*a*b*c
A.<u,v,r> = PolynomialRing(K)


def homogeneous_chart_coordinates(pivot):
    """Return homogeneous base coordinates on one affine chart."""

    return (
        (A(1), u, v),
        (u, A(1), v),
        (u, v, A(1)),
    )[pivot]


def affine_coordinate_indices(pivot):
    """Return global coordinates represented by the two affine variables."""

    return ((1, 2), (0, 2), (0, 1))[pivot]


def chart_equation(pivot, fiber_chart):
    """Return one exact affine cubic-pencil blow-up equation."""

    coordinates = homogeneous_chart_coordinates(pivot)
    f = F(*coordinates)
    g = G(*coordinates)
    return f + r*g if fiber_chart == "mu" else r*f + g


def affine_deck_action(generator, pivot, fiber_chart):
    """Derive a deck map between affine blow-up charts."""

    coordinates = homogeneous_chart_coordinates(pivot)
    images = P_IMAGES if generator == "P" else T_IMAGES
    homogeneous = tuple(entry(*coordinates) for entry in images)
    target_candidates = tuple(
        index for index, entry in enumerate(homogeneous) if entry.degree() == 0
    )
    assert len(target_candidates) == 1
    target_pivot = target_candidates[0]
    denominator = homogeneous[target_pivot]
    base_images = tuple(
        A(homogeneous[index] / denominator)
        for index in affine_coordinate_indices(target_pivot)
    )
    fiber_scale = omega^2 if generator == "P" and fiber_chart == "mu" else (
        omega if generator == "P" else K(1)
    )
    affine_images = (*base_images, A(fiber_scale*r))
    equation_unit = omega^2 if generator == "P" and fiber_chart == "mu" else K(1)
    pulled_target = chart_equation(target_pivot, fiber_chart)(*affine_images)
    assert pulled_target == equation_unit * chart_equation(pivot, fiber_chart)
    return target_pivot, affine_images


def compose_images(first, second):
    """Compose two affine polynomial maps in source coordinates."""

    return tuple(entry(*first) for entry in second)


def assert_dp9_deck_atlas():
    """Check all twelve chart maps, order-three laws, and commutation."""

    assert F(*P_IMAGES) == omega^2*F
    assert G(*P_IMAGES) == G
    assert F(*T_IMAGES) == F
    assert G(*T_IMAGES) == G
    actions = {
        (generator, pivot, fiber): affine_deck_action(generator, pivot, fiber)
        for generator in ("P", "T")
        for pivot in range(3)
        for fiber in ("mu", "nu")
    }
    identity = (u, v, r)
    for generator in ("P", "T"):
        for pivot in range(3):
            for fiber in ("mu", "nu"):
                current_pivot = pivot
                composed = identity
                for _ in range(3):
                    target_pivot, images = actions[(generator, current_pivot, fiber)]
                    composed = compose_images(composed, images)
                    current_pivot = target_pivot
                assert current_pivot == pivot
                assert composed == identity
    for pivot in range(3):
        for fiber in ("mu", "nu"):
            p_target, p_images = actions[("P", pivot, fiber)]
            pt_target, t_after_p = actions[("T", p_target, fiber)]
            t_target, t_images = actions[("T", pivot, fiber)]
            tp_target, p_after_t = actions[("P", t_target, fiber)]
            assert pt_target == tp_target
            assert compose_images(p_images, t_after_p) == compose_images(
                t_images, p_after_t
            )


S.<x1,x2,x3> = PolynomialRing(QQ)


def quotient_intersection(first, second, third):
    """Return the exact symmetric Schoen quotient intersection number."""

    indices = tuple(sorted((first, second, third)))
    return {
        (0, 0, 1): QQ(1)/3,
        (0, 1, 1): QQ(1)/3,
        (0, 1, 2): QQ(1),
    }.get(indices, QQ(0))


def formal_triple(left, middle, right):
    """Evaluate the quotient intersection tensor on formal divisors."""

    return sum(
        left[first]
        * middle[second]
        * right[third]
        * quotient_intersection(first, second, third)
        for first in range(3)
        for second in range(3)
        for third in range(3)
    )


def curvilinear_ch_three(factor, target_line_shift, twist):
    """Return the integrated twisted degree-three Chern character."""

    hyperplane = tuple(S(1 if index == factor else 0) for index in range(3))
    return (
        (QQ(target_line_shift^2)/2 - 9)
        * formal_triple(hyperplane, hyperplane, twist)
        -QQ(target_line_shift)/2 * formal_triple(hyperplane, twist, twist)
        +QQ(1)/3 * formal_triple(twist, twist, twist)
    )


def assert_curvilinear_rank_four_topology():
    """Exclude all current determinant-compatible pairs by exact index."""

    assert any(value % 2 for value in (-3, -3, 0))
    variables = (x1, x2, x3)
    bounded = tuple(product(range(-2, 3), repeat=3))
    for factor in (0, 1):
        hyperplane = tuple(1 if index == factor else 0 for index in range(3))
        complement = tuple(3*hyperplane[index] - variables[index] for index in range(3))
        assert curvilinear_ch_three(factor, 3, variables) + curvilinear_ch_three(
            factor, 3, complement
        ) == 0
        lawful = []
        for left in bounded:
            right = tuple(3*hyperplane[index] - left[index] for index in range(3))
            if right not in bounded:
                continue
            if (left[0]+left[1]) % 3 or (right[0]+right[1]) % 3:
                continue
            lawful.append((left, right))
        assert len(lawful) == 20
        assert all(
            curvilinear_ch_three(factor, 3, left)
            + curvilinear_ch_three(factor, 3, right)
            == 0
            for left, right in lawful
        )


def projective_section_dimension(degree):
    """Return the exact number of degree-``degree`` ternary monomials."""

    return 0 if degree < 0 else (degree + 1)*(degree + 2)//2


def curvilinear_cokernel_dimension(target_line_shift):
    """Return the graded dual-cokernel dimension from the exact resolution."""

    h = projective_section_dimension
    e = target_line_shift
    return 3*h(5-e) - h(3-e) - 3*h(4-e) + h(-e)


def assert_curvilinear_tier_b_topology():
    """Exclude every target-line shift allowed by the Tier B dimension bound."""

    e = polygen(QQ, 'e')
    low_shift_dimension = (
        3*(7-e)*(6-e)/2
        -(5-e)*(4-e)/2
        -3*(6-e)*(5-e)/2
        +(-e+1)*(-e+2)/2
    )
    assert low_shift_dimension == 9
    assert [curvilinear_cokernel_dimension(shift) for shift in (1, 2)] == [9, 9]
    assert [curvilinear_cokernel_dimension(shift) for shift in (3, 4, 5)] == [8, 6, 3]
    assert curvilinear_cokernel_dimension(6) == 0

    admissible = (3, 4, 5)
    bounded = tuple(product(range(-2, 3), repeat=3))
    bounded_set = set(bounded)
    constituent_types = tuple(product((0, 1), admissible))
    integral_type_count = 0
    pair_count = 0
    target_count = 0
    for (left_factor, left_shift), (right_factor, right_shift) in product(
        constituent_types,
        repeat=2,
    ):
        left_hyperplane = tuple(
            1 if index == left_factor else 0 for index in range(3)
        )
        right_hyperplane = tuple(
            1 if index == right_factor else 0 for index in range(3)
        )
        base_sum = tuple(
            left_shift*left_hyperplane[index]
            +right_shift*right_hyperplane[index]
            for index in range(3)
        )
        if any(value % 2 for value in base_sum):
            continue
        integral_type_count += 1
        required = tuple(value//2 for value in base_sum)
        for left_twist in bounded:
            right_twist = tuple(
                required[index] - left_twist[index]
                for index in range(3)
            )
            if right_twist not in bounded_set:
                continue
            quotient_index = curvilinear_ch_three(
                left_factor,
                left_shift,
                left_twist,
            ) + curvilinear_ch_three(
                right_factor,
                right_shift,
                right_twist,
            )
            pair_count += 1
            target_count += quotient_index in (S(3), S(-3))
    assert len(constituent_types)^2 == 36
    assert integral_type_count == 12
    assert pair_count == 340
    assert target_count == 0


def monomial_cokernel_dimension(generator_shifts, syzygy_shifts, target_shift):
    """Return one exact Betti-derived graded cokernel dimension."""

    h = projective_section_dimension
    return (
        sum(h(shift-target_shift) for shift in syzygy_shifts)
        -sum(h(shift-target_shift) for shift in generator_shifts)
        +h(-target_shift)
    )


def numeric_triple(left, middle, right):
    """Evaluate the quotient intersection tensor on rational coordinates."""

    return sum(
        QQ(left[first])
        *QQ(middle[second])
        *QQ(right[third])
        *quotient_intersection(first, second, third)
        for first in range(3)
        for second in range(3)
        for third in range(3)
    )


def monomial_ch_three(length, factor, target_shift, twist):
    """Return the exact twisted degree-three character for one Betti type."""

    hyperplane = tuple(1 if index == factor else 0 for index in range(3))
    return (
        (QQ(target_shift^2)/2-length)
        *numeric_triple(hyperplane, hyperplane, twist)
        -QQ(target_shift)/2*numeric_triple(hyperplane, twist, twist)
        +QQ(1)/3*numeric_triple(twist, twist, twist)
    )


def assert_monomial_tier_b_topology():
    """Reproduce the complete invariant-monomial topology frontier."""

    resolution_types = (
        ("L3", 3, (2, 2, 2), (3, 3)),
        ("L6", 6, (3, 3, 3, 3), (4, 4, 4)),
        ("L9", 9, (3, 4, 4, 4), (5, 5, 5)),
    )
    expected_dimensions = {
        "L3": (3, 3, 2, 0),
        "L6": (6, 6, 5, 3, 0),
        "L9": (9, 8, 6, 3, 0),
    }
    expected_shifts = {
        "L3": (-5, 0, 3, 4),
        "L6": (-7, 0, 3, 4, 5),
        "L9": (2, 3, 4, 5, 6),
    }
    for name, _, generators, syzygies in resolution_types:
        assert tuple(
            monomial_cokernel_dimension(generators, syzygies, shift)
            for shift in expected_shifts[name]
        ) == expected_dimensions[name]

    bounded = tuple(product(range(-2, 3), repeat=3))
    bounded_set = set(bounded)
    maximum_dimension = 8
    raw_count = 0
    determinant_descended = []
    for left, right in product(resolution_types, repeat=2):
        left_name, left_length, left_generators, left_syzygies = left
        right_name, right_length, right_generators, right_syzygies = right
        left_upper = max(left_syzygies)
        right_upper = max(right_syzygies)
        for left_factor, right_factor in product((0, 1), repeat=2):
            left_lower = -8 if left_factor != right_factor else -8-right_upper
            right_lower = -8 if left_factor != right_factor else -8-left_upper
            for left_shift in range(left_lower, left_upper+1):
                left_dimension = monomial_cokernel_dimension(
                    left_generators,
                    left_syzygies,
                    left_shift,
                )
                if not 0 < left_dimension <= maximum_dimension:
                    continue
                for right_shift in range(right_lower, right_upper+1):
                    right_dimension = monomial_cokernel_dimension(
                        right_generators,
                        right_syzygies,
                        right_shift,
                    )
                    if not 0 < right_dimension <= maximum_dimension:
                        continue
                    left_hyperplane = tuple(
                        1 if index == left_factor else 0 for index in range(3)
                    )
                    right_hyperplane = tuple(
                        1 if index == right_factor else 0 for index in range(3)
                    )
                    base_sum = tuple(
                        left_shift*left_hyperplane[index]
                        +right_shift*right_hyperplane[index]
                        for index in range(3)
                    )
                    if any(value % 2 for value in base_sum):
                        continue
                    required = tuple(value//2 for value in base_sum)
                    for left_twist in bounded:
                        right_twist = tuple(
                            required[index]-left_twist[index]
                            for index in range(3)
                        )
                        if right_twist not in bounded_set:
                            continue
                        quotient_index = monomial_ch_three(
                            left_length,
                            left_factor,
                            left_shift,
                            left_twist,
                        ) + monomial_ch_three(
                            right_length,
                            right_factor,
                            right_shift,
                            right_twist,
                        )
                        if abs(quotient_index) != 3:
                            continue
                        raw_count += 1
                        left_first = tuple(
                            -left_shift*left_hyperplane[index]+2*left_twist[index]
                            for index in range(3)
                        )
                        right_first = tuple(
                            -right_shift*right_hyperplane[index]+2*right_twist[index]
                            for index in range(3)
                        )
                        assert tuple(
                            left_first[index]+right_first[index]
                            for index in range(3)
                        ) == (0, 0, 0)
                        if (left_first[0]+left_first[1]) % 3:
                            continue
                        if (right_first[0]+right_first[1]) % 3:
                            continue
                        determinant_descended.append(
                            (
                                left_name,
                                left_factor,
                                left_shift,
                                left_twist,
                                right_name,
                                right_factor,
                                right_shift,
                                right_twist,
                            )
                        )
    assert raw_count == 1200
    assert len(determinant_descended) == 340
    available = {("L6", -6), ("L6", 0)}
    surviving = tuple(
        item
        for item in determinant_descended
        if (item[0], item[2]) in available and (item[4], item[6]) in available
    )
    assert len(surviving) == 40
    assert all(
        (item[3][0]+item[3][1]) % 3 == 0
        and (item[7][0]+item[7][1]) % 3 == 0
        for item in surviving
    )


assert_hilbert_burch(HB_U, GENERATORS_U)
assert_hilbert_burch(HB_V, GENERATORS_V)
assert_chern_data()
assert_projective_cocycles(
    HB_U,
    P_SOURCE_U,
    T_SOURCE_U,
    P_TARGET_U,
    T_TARGET_U,
    (omega, omega^2, K(1)),
    omega,
)
assert_projective_cocycles(
    HB_V,
    P_SOURCE_V,
    T_SOURCE_V,
    P_TARGET_V,
    T_TARGET_V,
    (omega^2, K(1), omega),
    omega^2,
)
assert_dp9_deck_atlas()
assert_curvilinear_rank_four_topology()
assert_curvilinear_tier_b_topology()
assert_monomial_tier_b_topology()


M3 = matrix(R, ((c, c), (-b, 0), (0, -a)))
M6 = matrix(R, ((a, 0, 0), (0, b, 0), (-b, -c, a), (0, 0, -c)))

M6_DUAL = matrix(
    R,
    ((a, 0, 0), (-c, b, a), (0, -c, 0), (0, 0, -b)),
)

P_TARGET_M6 = matrix(
    K,
    ((0, 0, 0, omega), (omega, 0, 0, 0), (0, 0, 1, 0), (0, omega, 0, 0)),
)
T_TARGET_M6 = diagonal_matrix(K, (omega, omega, 1, omega))
P_SOURCE_M6 = matrix(K, ((0, 0, -omega), (omega^2, 0, 0), (0, -1, 0)))
T_SOURCE_M6 = diagonal_matrix(K, (omega, omega^2, 1))

P_TARGET_M6_DUAL = matrix(
    K,
    (
        (0, 0, omega^2, 0),
        (0, 1, 0, 0),
        (0, 0, 0, omega^2),
        (omega^2, 0, 0, 0),
    ),
)
T_TARGET_M6_DUAL = diagonal_matrix(K, (omega^2, 1, omega^2, omega^2))
P_SOURCE_M6_DUAL = matrix(K, ((0, -omega^2, 0), (0, 0, omega), (-1, 0, 0)))
T_SOURCE_M6_DUAL = diagonal_matrix(K, (omega^2, omega, 1))


def monomial_exponents(degree):
    """Return the deterministic ternary monomial basis of one degree."""

    if degree < 0:
        return ()
    return tuple(
        exponent
        for exponent in product(range(degree+1), repeat=3)
        if sum(exponent) == degree
    )


def monomial_from_exponent(exponent):
    """Construct one exact polynomial monomial from its exponent triple."""

    return a^exponent[0]*b^exponent[1]*c^exponent[2]


def dual_presentation_sage(hilbert_burch, target_shift):
    """Build the exact graded dual presentation for a length-six ideal."""

    source_basis = tuple(
        (row, exponent)
        for row in range(4)
        for exponent in monomial_exponents(3-target_shift)
    )
    target_basis = tuple(
        (column, exponent)
        for column in range(3)
        for exponent in monomial_exponents(4-target_shift)
    )
    target_index = {label: index for index, label in enumerate(target_basis)}
    presentation = matrix(
        K,
        len(target_basis),
        len(source_basis),
        sparse=True,
    )
    for source_index, (row, exponent) in enumerate(source_basis):
        for column in range(3):
            for entry_exponent, coefficient in hilbert_burch[row, column].dict().items():
                target_exponent = tuple(
                    exponent[index]+entry_exponent[index]
                    for index in range(3)
                )
                presentation[target_index[(column, target_exponent)], source_index] += (
                    coefficient
                )
    return source_basis, target_basis, presentation


def dual_target_action_sage(target_basis, source_action, inverse_data):
    """Build one exact inverse-substitution action on the dual target."""

    index = {label: position for position, label in enumerate(target_basis)}
    dual = source_action.transpose()
    action = matrix(K, len(target_basis), len(target_basis), sparse=True)
    for source_index, (source_label, exponent) in enumerate(target_basis):
        target_exponent = [0, 0, 0]
        scalar = K(1)
        for power, (coordinate_scalar, coordinate_exponent) in zip(
            exponent,
            inverse_data,
        ):
            scalar *= coordinate_scalar^power
            target_exponent = [
                target_exponent[index]+power*coordinate_exponent[index]
                for index in range(3)
            ]
        target_exponent = tuple(target_exponent)
        for target_label in range(3):
            action[index[(target_label, target_exponent)], source_index] += (
                dual[target_label, source_label]*scalar
            )
    return action


def quotient_decomposition_sage(presentation):
    """Build one normalized exact sparse image basis for a presentation."""

    image_basis = {}
    for column in range(presentation.ncols()):
        vector = {
            row: presentation[row, column]
            for row in range(presentation.nrows())
            if presentation[row, column] != 0
        }
        reduced = sparse_reduce_sage(vector, image_basis)
        if not reduced:
            continue
        pivot = min(reduced)
        leading = reduced[pivot]
        image_basis[pivot] = {
            index: value/leading for index, value in reduced.items()
        }
    representatives = tuple(
        index for index in range(presentation.nrows()) if index not in image_basis
    )
    return image_basis, representatives


def sparse_reduce_sage(vector, image_basis):
    """Reduce one sparse vector modulo a normalized exact image basis."""

    result = dict(vector)
    for pivot in sorted(image_basis):
        coefficient = result.get(pivot, K(0))
        if coefficient == 0:
            continue
        for index, value in image_basis[pivot].items():
            updated = result.get(index, K(0))-coefficient*value
            if updated == 0:
                result.pop(index, None)
            else:
                result[index] = updated
    return result


def sparse_matrix_images_sage(target_action):
    """Return sparse column images of one exact target matrix."""

    return tuple(
        {
            row: target_action[row, column]
            for row in range(target_action.nrows())
            if target_action[row, column] != 0
        }
        for column in range(target_action.ncols())
    )


def apply_sparse_action_sage(vector, target_images):
    """Apply exact sparse target images to one sparse vector."""

    result = {}
    for source, coefficient in vector.items():
        for target, value in target_images[source].items():
            updated = result.get(target, K(0))+coefficient*value
            if updated == 0:
                result.pop(target, None)
            else:
                result[target] = updated
    return result


def quotient_action_sage(decomposition, target_action):
    """Descend one target action through a reused exact decomposition."""

    image_basis, representatives = decomposition
    target_images = sparse_matrix_images_sage(target_action)
    assert all(
        not sparse_reduce_sage(
            apply_sparse_action_sage(vector, target_images),
            image_basis,
        )
        for vector in image_basis.values()
    )
    quotient = matrix(K, len(representatives), len(representatives), sparse=True)
    for column, representative in enumerate(representatives):
        reduced = sparse_reduce_sage(
            target_images[representative],
            image_basis,
        )
        for row, target in enumerate(representatives):
            quotient[row, column] = reduced.get(target, K(0))
    return quotient, representatives


def length_six_quotient_actions(hilbert_burch, source_p, source_t, target_shift):
    """Return exact P/T actions on one length-six graded cokernel."""

    _, target_basis, presentation = dual_presentation_sage(
        hilbert_burch,
        target_shift,
    )
    inverse_p = (
        (K(1), (0, 0, 1)),
        (omega^2, (1, 0, 0)),
        (omega, (0, 1, 0)),
    )
    inverse_t = (
        (K(1), (1, 0, 0)),
        (omega^2, (0, 1, 0)),
        (omega, (0, 0, 1)),
    )
    full_p = dual_target_action_sage(target_basis, source_p, inverse_p)
    full_t = dual_target_action_sage(target_basis, source_t, inverse_t)
    decomposition = quotient_decomposition_sage(presentation)
    quotient_p, representatives = quotient_action_sage(decomposition, full_p)
    quotient_t, t_representatives = quotient_action_sage(decomposition, full_t)
    assert representatives == t_representatives
    return target_basis, representatives, full_p, full_t, quotient_p, quotient_t


def length_six_locally_free_characters(
    hilbert_burch,
    source_p,
    source_t,
    target_p,
    target_t,
    target_shift,
    action_data=None,
):
    """Return common characters passing exact projective sheaf gates."""

    if action_data is None:
        action_data = length_six_quotient_actions(
            hilbert_burch,
            source_p,
            source_t,
            target_shift,
        )
    target_basis, representatives, full_p, full_t, quotient_p, quotient_t = action_data
    quotient_identity = identity_matrix(K, quotient_p.nrows())
    characters = []
    projective_characters = []
    source_central = diagonal_matrix(
        R,
        tuple(omega^4 for _ in range(hilbert_burch.ncols())),
    )
    target_central = diagonal_matrix(
        R,
        tuple(omega^3 for _ in range(hilbert_burch.nrows())),
    )
    middle_central = diagonal_matrix(
        R,
        (*tuple(omega^3 for _ in range(hilbert_burch.nrows())), omega^target_shift),
    )
    for p_character, t_character in product((1, omega, omega^2), repeat=2):
        equations = (quotient_p-p_character*quotient_identity).stack(
            quotient_t-t_character*quotient_identity
        )
        for quotient_vector in equations.right_kernel().basis():
            full_values = [K(0) for _ in target_basis]
            for value, representative in zip(
                quotient_vector,
                representatives,
            ):
                full_values[representative] = value
            full_vector = vector(K, full_values)
            if full_p*full_vector != p_character*full_vector:
                continue
            if full_t*full_vector != t_character*full_vector:
                continue
            extension = []
            for column in range(3):
                extension.append(
                    sum(
                        full_values[index]*monomial_from_exponent(exponent)
                        for index, (owner, exponent) in enumerate(target_basis)
                        if owner == column
                    )
                )
            relation = relation_matrix(hilbert_burch, extension)
            if all(
                matrix(
                    K,
                    tuple(
                        tuple(entry(*point) for entry in row)
                        for row in relation.rows()
                    ),
                ).rank() == 3
                for point in ((1, 0, 0), (0, 1, 0), (0, 0, 1))
            ):
                characters.append((p_character, t_character))
                minors = column_maximal_minors(relation)
                if all(
                    R.ideal(
                        tuple(minor.subs({pivot: 1}) for minor in minors)
                    ).is_one()
                    for pivot in (a, b, c)
                ):
                    p_middle = middle_action(target_p, p_character)
                    t_middle = middle_action(target_t, t_character)
                    assert source_p.transpose()*relation == (
                        transform_matrix(relation, P_IMAGES)*p_middle
                    )
                    assert source_t.transpose()*relation == (
                        transform_matrix(relation, T_IMAGES)*t_middle
                    )
                    assert p_middle^3 == identity_matrix(R, 5)
                    assert t_middle^3 == identity_matrix(R, 5)
                    assert p_middle*middle_central == middle_central*p_middle
                    assert t_middle*middle_central == middle_central*t_middle
                    assert p_middle*t_middle == middle_central*t_middle*p_middle
                    assert source_p*source_t == (
                        source_central.inverse()*source_t*source_p
                    )
                    assert target_p*target_t == (
                        target_central.inverse()*target_t*target_p
                    )
                    assert transform_matrix(relation, CENTRAL_IMAGES) == (
                        source_central*relation*middle_central.inverse()
                    )
                    projective_characters.append((p_character, t_character))
    return tuple(characters), tuple(projective_characters)


def assert_length_six_shift_frontier():
    """Reproduce the two surviving shifts and their exact common eigenrays."""

    schemes = (
        (
            M6,
            P_SOURCE_M6,
            T_SOURCE_M6,
            P_TARGET_M6,
            T_TARGET_M6,
            frozenset((p_character, omega^2) for p_character in (1, omega, omega^2)),
        ),
        (
            M6_DUAL,
            P_SOURCE_M6_DUAL,
            T_SOURCE_M6_DUAL,
            P_TARGET_M6_DUAL,
            T_TARGET_M6_DUAL,
            frozenset((p_character, omega) for p_character in (1, omega, omega^2)),
        ),
    )
    for hilbert_burch, source_p, source_t, target_p, target_t, expected in schemes:
        assert hilbert_burch*source_p == target_p*transform_matrix(
            hilbert_burch,
            P_IMAGES,
        )
        assert hilbert_burch*source_t == target_t*transform_matrix(
            hilbert_burch,
            T_IMAGES,
        )
        commuting_shifts = []
        action_data_by_shift = {}
        for target_shift in (-7, -6, -1, 0, 1):
            action_data = length_six_quotient_actions(
                hilbert_burch,
                source_p,
                source_t,
                target_shift,
            )
            action_data_by_shift[target_shift] = action_data
            *_, quotient_p, quotient_t = action_data
            assert quotient_p^3 == identity_matrix(K, quotient_p.nrows())
            assert quotient_t^3 == identity_matrix(K, quotient_t.nrows())
            if quotient_p*quotient_t == quotient_t*quotient_p:
                commuting_shifts.append(target_shift)
        assert tuple(commuting_shifts) == (-6, 0)
        for target_shift in commuting_shifts:
            support_characters, projective_characters = (
                length_six_locally_free_characters(
                    hilbert_burch,
                    source_p,
                    source_t,
                    target_p,
                    target_t,
                    target_shift,
                    action_data_by_shift[target_shift],
                )
            )
            assert frozenset(support_characters) == expected
            assert frozenset(projective_characters) == expected


assert_length_six_shift_frontier()

assert tuple(M3_minors := unsigned_maximal_minors(M3)) == (a*b, -a*c, b*c)
assert tuple(M6_minors := unsigned_maximal_minors(M6)) == (
    -b^2*c, a*c^2, -a*b*c, a^2*b
)

N = matrix(R, ((0, 1), (0, 0)))
I = identity_matrix(R, 2)
potentials = (a, b, c)


def constituent_transition(left, right):
    """Return the exact unipotent transition used by the baseline."""

    return I + (potentials[left] - potentials[right]) * N


def outer_transition(left, right):
    """Return the four-by-four split block transition."""

    g = constituent_transition(left, right)
    q_left = potentials[left] * I
    q_right = potentials[right] * I
    phi = q_left * g - g * q_right
    return block_matrix([[g, phi], [zero_matrix(R, 2), g]])


for left in range(3):
    for middle in range(3):
        for right in range(3):
            if len({left, middle, right}) == 3:
                assert outer_transition(left, right) == (
                    outer_transition(left, middle) * outer_transition(middle, right)
                )

print("hilbert_burch_I3: pass")
print("hilbert_burch_I6: pass")
print("split_rank_four_transition_cocycle: pass")
print("split_rank_four_status: excluded")
print("curvilinear_hilbert_burch: pass")
print("curvilinear_fitting_cover: pass")
print("curvilinear_chern_data: pass")
print("curvilinear_projective_cocycles: pass")
print("dp9_deck_atlas: pass")
print("curvilinear_descent_status: conditional_on_published_free_quotient")
print("curvilinear_rank_four_topology: excluded_index_zero")
print("curvilinear_tier_b_topology: excluded_no_index_three")
print("monomial_tier_b_topology_counts: pass")
print("monomial_length_six_shift_frontier: pass")
print("monomial_length_six_constituents: pass")
