"""Independent exact SageMath checks for the computable carrier frontier."""

from itertools import combinations


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


M3 = matrix(R, ((c, c), (-b, 0), (0, -a)))
M6 = matrix(R, ((a, 0, 0), (0, b, 0), (-b, -c, a), (0, 0, -c)))

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
