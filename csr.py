def make_csr(A) -> tuple[list, list, list]:
    rows = len(A)
    cols = len(A[0])

    row_ptr = [0]
    col_idx = []
    val = []

    nnz = 0

    for i in range(rows):
        for j in range(cols):
            if A[i][j] != 0:
                nnz += 1
                val.append(A[i][j])
                col_idx.append(j)
        row_ptr.append(nnz)

    return (row_ptr, col_idx, val)