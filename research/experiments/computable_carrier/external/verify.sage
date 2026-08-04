"""Independent exact SageMath checks for the computable carrier frontier."""

R.<a,b,c> = PolynomialRing(QQ)


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


M3 = matrix(R, ((c, c), (-b, 0), (0, -a)))
M6 = matrix(R, ((a, 0, 0), (0, b, 0), (-b, -c, a), (0, 0, -c)))

assert tuple(M3_minors := unsigned_maximal_minors(M3)) == (a*b, -a*c, b*c)
assert tuple(M6_minors := unsigned_maximal_minors(M6)) == (
    b^2*c, -a*c^2, a*b*c, -a^2*b
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
