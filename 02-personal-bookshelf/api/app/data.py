from app.models import Book, BookStatus

# Seed ids are readable slugs so they are pleasant to curl by hand. Books
# created through POST get a uuid4 hex instead - ids are opaque strings, so
# mixing the two formats is fine.
SEED: list[Book] = [
    Book(id="dune", title="Dune", author="Frank Herbert", status=BookStatus.READ, rating=5),
    Book(id="piranesi", title="Piranesi", author="Susanna Clarke", status=BookStatus.READING),
    Book(id="station-eleven", title="Station Eleven", author="Emily St. John Mandel", status=BookStatus.READ, rating=4),
    Book(id="left-hand-of-darkness", title="The Left Hand of Darkness", author="Ursula K. Le Guin", status=BookStatus.READ, rating=5),
    Book(id="project-hail-mary", title="Project Hail Mary", author="Andy Weir", status=BookStatus.WANT),
    Book(id="klara-and-the-sun", title="Klara and the Sun", author="Kazuo Ishiguro", status=BookStatus.READ, rating=3),
    Book(id="the-overstory", title="The Overstory", author="Richard Powers", status=BookStatus.READING),
    Book(id="solaris", title="Solaris", author="Stanislaw Lem", status=BookStatus.WANT),
    Book(id="a-memory-called-empire", title="A Memory Called Empire", author="Arkady Martine", status=BookStatus.READ, rating=4),
    Book(id="the-dispossessed", title="The Dispossessed", author="Ursula K. Le Guin", status=BookStatus.WANT),
    Book(id="never-let-me-go", title="Never Let Me Go", author="Kazuo Ishiguro", status=BookStatus.READ, rating=4),
    Book(id="annihilation", title="Annihilation", author="Jeff VanderMeer", status=BookStatus.READ, rating=3),
    Book(id="three-body-problem", title="The Three-Body Problem", author="Liu Cixin", status=BookStatus.READING),
    Book(id="exhalation", title="Exhalation", author="Ted Chiang", status=BookStatus.READ, rating=5),
    Book(id="sea-of-tranquility", title="Sea of Tranquility", author="Emily St. John Mandel", status=BookStatus.WANT),
]

# The live store. Mutable - POST/PUT/DELETE change it, and it resets on restart.
BOOKS: list[Book] = []


def reset_books() -> None:
    """Restore BOOKS to the seeded set. Called on import and before each test."""
    BOOKS.clear()
    BOOKS.extend(book.model_copy(deep=True) for book in SEED)


reset_books()
