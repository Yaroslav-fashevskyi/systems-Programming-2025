# systems-Programming-2025

python -c "import sqlite3; con=sqlite3.connect('test.db'); print([r[0] for r in con.execute('SELECT name FROM sqlite_master WHERE type=\'table\' ORDER BY name').fetchall()]); con.close()"
