from scripts.apply_prd_submission_metadata import apply_metadata


def test_apply_metadata_preserves_abstract_and_keywords():
    tex = r"""\title{Test title}

\author{Placeholder}
\affiliation{Placeholder affiliation}

\begin{abstract}
The abstract must survive author substitution.
\end{abstract}

\keywords{Kerr, scattering}

\maketitle
"""
    metadata = {
        "submission": {"corresponding_author": "A. Author"},
        "authors": [
            {
                "name": "A. Author",
                "email": "author@example.edu",
                "affiliations": ["Department of Physics"],
            }
        ],
    }

    updated = apply_metadata(tex, metadata)

    assert updated.count(r"\begin{abstract}") == 1
    assert updated.count(r"\end{abstract}") == 1
    assert "The abstract must survive author substitution." in updated
    assert r"\keywords{Kerr, scattering}" in updated
    assert r"\author{A. Author}" in updated
    assert r"\email{author@example.edu}" in updated
    assert r"\author{Placeholder}" not in updated
