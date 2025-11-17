Development Guide
=================

This guide provides essential information for developers contributing to Flash Sheet, including coding standards, development workflow, testing practices, and deployment procedures.

Getting Started
---------------

Development Environment Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Prerequisites:**

- Python 3.7+
- Git
- Virtual environment tool (venv, conda, or virtualenv)
- Qt development tools (for PySide6)

**Clone and Setup:**

.. code-block:: bash

    git clone https://github.com/your-org/flash-sheet.git
    cd flash-sheet
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    pip install -r requirements-dev.txt

**Development Dependencies:**

.. code-block:: txt

    # requirements-dev.txt
    pytest>=6.0.0
    pytest-cov>=2.0.0
    black>=21.0.0
    flake8>=3.9.0
    mypy>=0.800
    sphinx>=4.0.0
    tox>=3.0.0

Project Structure
-----------------

Code Organization
~~~~~~~~~~~~~~~~~

::

    flash-sheet/
    ├── main.py                 # Application entry point
    ├── app/                    # Main application package
    │   ├── __init__.py
    │   ├── main_window.py      # Main window implementation
    │   ├── data_handler.py     # Data management core
    │   └── widgets/            # UI components
    │       ├── __init__.py
    │       ├── data_view.py    # Data table view
    │       ├── graphics_view.py # Chart view
    │       └── dialogs/        # Dialog windows
    ├── core/                   # Business logic
    │   ├── __init__.py
    │   ├── data_loader.py      # Data loading utilities
    │   ├── data_exporter.py    # Export functionality
    │   ├── join_manager.py     # Data join operations
    │   └── pivot_manager.py    # Pivot table operations
    ├── tests/                  # Test suite
    │   ├── __init__.py
    │   ├── unit/               # Unit tests
    │   ├── integration/        # Integration tests
    │   └── fixtures/           # Test data
    ├── docs/                   # Documentation
    │   ├── conf.py
    │   ├── index.rst
    │   └── ...
    ├── scripts/                # Utility scripts
    ├── examples/               # Example code and data
    └── requirements.txt

Coding Standards
----------------

Python Style Guide
~~~~~~~~~~~~~~~~~~

**Follow PEP 8 with these additions:**

- Maximum line length: 100 characters
- Use type hints for function parameters and return values
- Use docstrings for all public methods
- Use descriptive variable names
- Prefer f-strings over .format() and %

**Code Formatting:**

.. code-block:: bash

    # Format code with Black
    black --line-length 100 .

    # Check style with Flake8
    flake8 --max-line-length 100 .

**Type Checking:**

.. code-block:: bash

    # Run mypy for static type checking
    mypy --ignore-missing-imports .

Docstring Format
~~~~~~~~~~~~~~~~

Use Google-style docstrings:

.. code-block:: python

    def load_file(self, file_path: str, encoding: str = 'utf-8') -> pd.DataFrame:
        """Load data from a file.

        Args:
            file_path: Path to the data file to load.
            encoding: Text encoding to use for reading the file.

        Returns:
            A pandas DataFrame containing the loaded data.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            UnsupportedFormatError: If the file format is not supported.
        """
        pass

Naming Conventions
~~~~~~~~~~~~~~~~~~

- **Classes**: PascalCase (DataHandler, MainWindow)
- **Methods/Functions**: snake_case (load_file, export_data)
- **Constants**: UPPER_CASE (MAX_CHUNK_SIZE, DEFAULT_ENCODING)
- **Private members**: Leading underscore (_internal_method)
- **Modules**: snake_case (data_handler.py, main_window.py)

Error Handling
~~~~~~~~~~~~~~

**Exception Hierarchy:**

.. code-block:: python

    class FlashSheetError(Exception):
        """Base exception for Flash Sheet."""
        pass

    class DataError(FlashSheetError):
        """Data-related errors."""
        pass

    class FileError(DataError):
        """File operation errors."""
        pass

**Error Handling Pattern:**

.. code-block:: python

    try:
        data = self.load_file(file_path)
    except FileNotFoundError:
        raise FileError(f"File not found: {file_path}")
    except UnsupportedFormatError as e:
        self.logger.error(f"Unsupported format: {e}")
        raise
    except Exception as e:
        self.logger.error(f"Unexpected error: {e}")
        raise DataError("Failed to load data") from e

Development Workflow
--------------------

Git Workflow
~~~~~~~~~~~~

**Branching Strategy:**

- ``main``: Production-ready code
- ``develop``: Integration branch for features
- ``feature/*``: Feature branches
- ``bugfix/*``: Bug fix branches
- ``release/*``: Release preparation

**Commit Messages:**

.. code-block:: text

    type(scope): description

    [optional body]

    [optional footer]

**Types:**

- ``feat``: New features
- ``fix``: Bug fixes
- ``docs``: Documentation changes
- ``style``: Code style changes
- ``refactor``: Code refactoring
- ``test``: Test additions/modifications
- ``chore``: Maintenance tasks

**Example:**

.. code-block:: text

    feat(data-loader): Add support for Parquet files

    - Implement Parquet file detection
    - Add fastparquet dependency
    - Update format validation

    Closes #123

Pull Request Process
~~~~~~~~~~~~~~~~~~~~

1. **Create Feature Branch:**

   .. code-block:: bash

       git checkout -b feature/new-feature develop

2. **Make Changes:**

   - Write code following standards
   - Add/update tests
   - Update documentation

3. **Run Quality Checks:**

   .. code-block:: bash

       # Run all tests
       pytest

       # Check code quality
       black --check .
       flake8 .
       mypy .

4. **Commit Changes:**

   .. code-block:: bash

       git add .
       git commit -m "feat: Add new feature"

5. **Push and Create PR:**

   .. code-block:: bash

       git push origin feature/new-feature

6. **Code Review:**

   - Address review comments
   - Ensure CI passes
   - Get approval

7. **Merge:**

   - Squash merge to develop
   - Delete feature branch

Testing
-------

Test Structure
~~~~~~~~~~~~~~

**Test Organization:**

::

    tests/
    ├── unit/                    # Unit tests
    │   ├── test_data_handler.py
    │   ├── test_main_window.py
    │   └── ...
    ├── integration/            # Integration tests
    │   ├── test_file_loading.py
    │   ├── test_export_workflow.py
    │   └── ...
    ├── fixtures/               # Test data
    │   ├── sample_data.csv
    │   ├── test_template.xlsx
    │   └── ...
    └── conftest.py             # Pytest configuration

Unit Testing
~~~~~~~~~~~~

**Example Unit Test:**

.. code-block:: python

    import pytest
    from app.data_handler import DataHandler

    class TestDataHandler:
        def test_load_csv_file(self, tmp_path):
            # Create test CSV file
            csv_file = tmp_path / "test.csv"
            csv_file.write_text("name,age\nAlice,30\nBob,25\n")

            # Test loading
            handler = DataHandler()
            df = handler.load_file(str(csv_file))

            assert len(df) == 2
            assert list(df.columns) == ['name', 'age']
            assert df.iloc[0]['name'] == 'Alice'

        def test_unsupported_format(self):
            handler = DataHandler()

            with pytest.raises(UnsupportedFormatError):
                handler.load_file("test.unsupported")

Integration Testing
~~~~~~~~~~~~~~~~~~~

**End-to-End Test Example:**

.. code-block:: python

    def test_complete_data_workflow(self, tmp_path):
        # Setup test data
        csv_file = tmp_path / "input.csv"
        csv_file.write_text("id,name,value\n1,A,100\n2,B,200\n")

        output_file = tmp_path / "output.xlsx"

        # Execute workflow
        handler = DataHandler()
        data = handler.load_file(str(csv_file))

        # Apply some transformation
        data['doubled'] = data['value'] * 2

        # Export
        handler.export_data(data, 'excel', str(output_file))

        # Verify
        assert output_file.exists()
        reloaded = handler.load_file(str(output_file))
        assert len(reloaded) == 2
        assert 'doubled' in reloaded.columns

Test Data Management
~~~~~~~~~~~~~~~~~~~~

**Fixture Usage:**

.. code-block:: python

    @pytest.fixture
    def sample_dataframe():
        return pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'value': [100, 200, 300]
        })

    @pytest.fixture
    def temp_csv_file(tmp_path, sample_dataframe):
        file_path = tmp_path / "test.csv"
        sample_dataframe.to_csv(file_path, index=False)
        return str(file_path)

**Test Running:**

.. code-block:: bash

    # Run all tests
    pytest

    # Run with coverage
    pytest --cov=app --cov-report=html

    # Run specific test
    pytest tests/unit/test_data_handler.py::TestDataHandler::test_load_csv_file

    # Run tests matching pattern
    pytest -k "csv"

Continuous Integration
~~~~~~~~~~~~~~~~~~~~~~

**GitHub Actions Configuration:**

.. code-block:: yaml

    name: CI

    on: [push, pull_request]

    jobs:
      test:
        runs-on: ubuntu-latest
        strategy:
          matrix:
            python-version: [3.7, 3.8, 3.9]

        steps:
        - uses: actions/checkout@v2
        - name: Set up Python ${{ matrix.python-version }}
          uses: actions/setup-python@v2
          with:
            python-version: ${{ matrix.python-version }}
        - name: Install dependencies
          run: |
            pip install -r requirements.txt
            pip install -r requirements-dev.txt
        - name: Run tests
          run: pytest --cov=app --cov-report=xml
        - name: Upload coverage
          uses: codecov/codecov-action@v1

Documentation
-------------

Building Documentation
~~~~~~~~~~~~~~~~~~~~~~

**Sphinx Setup:**

.. code-block:: bash

    # Install documentation dependencies
    pip install sphinx sphinx-rtd-theme

    # Build HTML documentation
    cd docs
    make html

**Documentation Structure:**

- **User Guide**: End-user documentation
- **Developer Guide**: API reference and development info
- **Release Notes**: Version change logs

Writing Documentation
~~~~~~~~~~~~~~~~~~~~~

**reStructuredText (RST) Format:**

.. code-block:: rst

    Section Title
    =============

    Subsection
    ----------

    **Bold text**, *italic text*, ``code``

    .. code-block:: python

        # Code example
        def hello_world():
            print("Hello, World!")

    :param name: Description of parameter
    :returns: Description of return value

**Documentation Testing:**

.. code-block:: bash

    # Test documentation build
    cd docs
    make doctest

    # Check links
    make linkcheck

Deployment
----------

Packaging
~~~~~~~~~

**PyInstaller for Standalone Executable:**

.. code-block:: bash

    # Install PyInstaller
    pip install pyinstaller

    # Create executable
    pyinstaller --onefile --windowed main.py

**Setup.py Configuration:**

.. code-block:: python

    from setuptools import setup, find_packages

    setup(
        name="flash-sheet",
        version="1.0.0",
        packages=find_packages(),
        install_requires=[
            'pandas>=1.3.0',
            'PySide6>=6.0.0',
            'openpyxl>=3.0.0',
            'numpy>=1.21.0',
        ],
        entry_points={
            'console_scripts': [
                'flash-sheet=main:main',
            ],
        },
    )

Release Process
~~~~~~~~~~~~~~~

**Version Management:**

1. **Update Version:**

   .. code-block:: python

       # In __init__.py or version.py
       __version__ = "1.1.0"

2. **Update Changelog:**

   .. code-block:: text

       # CHANGELOG.md
       ## [1.1.0] - 2025-11-17
       ### Added
       - New feature X
       ### Fixed
       - Bug fix Y

3. **Create Release Branch:**

   .. code-block:: bash

       git checkout -b release/1.1.0 develop

4. **Run Final Tests:**

   .. code-block:: bash

       tox  # Run tests across multiple Python versions

5. **Build Documentation:**

   .. code-block:: bash

       cd docs && make html

6. **Create GitHub Release:**

   - Tag the release: ``git tag -a v1.1.0``
   - Push tags: ``git push origin v1.1.0``
   - Create release on GitHub with changelog

Distribution
~~~~~~~~~~~~

**PyPI Upload:**

.. code-block:: bash

    # Build distribution
    python setup.py sdist bdist_wheel

    # Upload to PyPI
    twine upload dist/*

**Platform-Specific Builds:**

- **Windows**: Use PyInstaller on Windows
- **macOS**: Build on macOS for native app
- **Linux**: Create .deb or .rpm packages

Performance Optimization
------------------------

Memory Management
~~~~~~~~~~~~~~~~~

**Large Dataset Handling:**

.. code-block:: python

    class MemoryEfficientLoader:
        def load_large_csv(self, file_path, chunk_size=10000):
            """Load large CSV files in chunks."""
            chunks = []
            for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                # Process chunk
                processed = self.process_chunk(chunk)
                chunks.append(processed)

            return pd.concat(chunks, ignore_index=True)

**Memory Monitoring:**

.. code-block:: python

    import psutil
    import os

    def get_memory_usage():
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # MB

UI Responsiveness
~~~~~~~~~~~~~~~~~

**Background Processing:**

.. code-block:: python

    from PySide6.QtCore import QThread, Signal

    class DataLoadWorker(QThread):
        finished = Signal(object)
        error = Signal(str)
        progress = Signal(int)

        def __init__(self, file_path):
            super().__init__()
            self.file_path = file_path

        def run(self):
            try:
                # Load data in background
                data = self.load_data()
                self.finished.emit(data)
            except Exception as e:
                self.error.emit(str(e))

**Usage:**

.. code-block:: python

    worker = DataLoadWorker(file_path)
    worker.finished.connect(self.on_data_loaded)
    worker.error.connect(self.on_load_error)
    worker.start()

Code Profiling
~~~~~~~~~~~~~~

**Performance Profiling:**

.. code-block:: python

    import cProfile
    import pstats

    def profile_function(func, *args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()

        result = func(*args, **kwargs)

        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumulative')
        stats.print_stats(20)  # Top 20 functions

        return result

**Memory Profiling:**

.. code-block:: python

    from memory_profiler import profile

    @profile
    def memory_intensive_function():
        # Function to profile
        pass

Security Considerations
-----------------------

Input Validation
~~~~~~~~~~~~~~~~

**Data Sanitization:**

.. code-block:: python

    def sanitize_filename(filename):
        """Remove dangerous characters from filename."""
        import re
        return re.sub(r'[<>:"/\\|?*]', '', filename)

**SQL Injection Prevention:**

.. code-block:: python

    # Use parameterized queries
    query = "SELECT * FROM table WHERE id = ?"
    df = pd.read_sql(query, connection, params=(user_id,))

Secure Configuration
~~~~~~~~~~~~~~~~~~~~

**Sensitive Data Handling:**

.. code-block:: python

    import os

    class SecureConfig:
        def get_database_url(self):
            # Use environment variables for sensitive data
            return os.getenv('DATABASE_URL')

        def get_api_key(self):
            return os.getenv('API_KEY')

**File Permissions:**

.. code-block:: bash

    # Set appropriate permissions
    chmod 600 config/secrets.json

Contributing Guidelines
-----------------------

Issue Reporting
~~~~~~~~~~~~~~~

**Bug Report Template:**

.. code-block:: text

    ## Bug Report

    **Version:** 1.0.0
    **OS:** Windows 10
    **Python:** 3.8.5

    **Description:**
    Brief description of the bug

    **Steps to Reproduce:**
    1. Step 1
    2. Step 2
    3. Step 3

    **Expected Behavior:**
    What should happen

    **Actual Behavior:**
    What actually happens

    **Additional Context:**
    Screenshots, logs, etc.

Feature Requests
~~~~~~~~~~~~~~~~

**Feature Request Template:**

.. code-block:: text

    ## Feature Request

    **Problem:**
    Description of the problem this feature would solve

    **Solution:**
    Description of the proposed solution

    **Alternatives:**
    Alternative solutions considered

    **Additional Context:**
    Mockups, examples, etc.

Code Contribution
~~~~~~~~~~~~~~~~~

**Pull Request Checklist:**

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows style guidelines
- [ ] Commit messages follow convention
- [ ] CI passes
- [ ] Reviewed by at least one maintainer

**Code Review Process:**

1. **Automated Checks:** CI runs tests and quality checks
2. **Peer Review:** At least one maintainer reviews code
3. **Discussion:** Address review comments
4. **Approval:** Maintainers approve PR
5. **Merge:** PR is merged to develop branch

Community
---------

Communication Channels
~~~~~~~~~~~~~~~~~~~~~~

- **GitHub Issues:** Bug reports and feature requests
- **GitHub Discussions:** General questions and discussions
- **Email:** developer@flash-sheet.org for security issues

Code of Conduct
~~~~~~~~~~~~~~~

**Our Standards:**

- Be respectful and inclusive
- Focus on constructive feedback
- Accept responsibility for mistakes
- Show empathy towards other community members

**Unacceptable Behavior:**

- Harassment or discrimination
- Personal attacks
- Spam or off-topic content
- Sharing private information

License
-------

**MIT License**

Copyright (c) 2025 Flash Sheet Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.