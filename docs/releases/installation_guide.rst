Installation Guide
==================

This guide provides step-by-step instructions for installing Flash Sheet on different operating systems.

System Requirements
-------------------

Minimum Requirements
~~~~~~~~~~~~~~~~~~~~

- **Operating System**: Windows 10, macOS 10.15, or Ubuntu 18.04+
- **Processor**: 1 GHz or faster processor
- **Memory**: 4 GB RAM (8 GB recommended)
- **Storage**: 500 MB available disk space
- **Display**: 1024 x 768 resolution or higher

Recommended Requirements
~~~~~~~~~~~~~~~~~~~~~~~~

- **Operating System**: Windows 11, macOS 12+, or Ubuntu 20.04+
- **Processor**: Multi-core processor (Intel i5 or equivalent)
- **Memory**: 8 GB RAM or more
- **Storage**: 1 GB available disk space
- **Display**: 1920 x 1080 resolution or higher

Python Requirements
~~~~~~~~~~~~~~~~~~~

- **Python Version**: 3.7 or higher
- **Pip**: Latest version recommended
- **Virtual Environment**: venv, conda, or virtualenv

Installation Methods
--------------------

Method 1: Standalone Executable (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Windows:**

1. Download the Windows installer (``flash-sheet-setup.exe``) from the releases page
2. Run the installer as administrator
3. Follow the installation wizard
4. Launch Flash Sheet from the Start menu or desktop shortcut

**macOS:**

1. Download the macOS disk image (``flash-sheet.dmg``) from the releases page
2. Open the disk image
3. Drag Flash Sheet to the Applications folder
4. Launch Flash Sheet from Applications or Spotlight

**Linux:**

1. Download the AppImage file (``flash-sheet.AppImage``) from the releases page
2. Make the file executable:

   .. code-block:: bash

       chmod +x flash-sheet.AppImage

3. Run the application:

   .. code-block:: bash

       ./flash-sheet.AppImage

Method 2: Python Package Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Using pip (Recommended for Python Users):**

1. Ensure Python 3.7+ is installed:

   .. code-block:: bash

       python --version

2. Install Flash Sheet:

   .. code-block:: bash

       pip install flash-sheet

3. Launch the application:

   .. code-block:: bash

       flash-sheet

**From Source Code:**

1. Clone the repository:

   .. code-block:: bash

       git clone https://github.com/your-org/flash-sheet.git
       cd flash-sheet

2. Create a virtual environment:

   .. code-block:: bash

       python -m venv venv
       source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:

   .. code-block:: bash

       pip install -r requirements.txt

4. Run the application:

   .. code-block:: bash

       python main.py

Method 3: Conda Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Using conda:**

1. Install Miniconda or Anaconda
2. Create a new environment:

   .. code-block:: bash

       conda create -n flash-sheet python=3.8
       conda activate flash-sheet

3. Install Flash Sheet:

   .. code-block:: bash

       conda install -c your-channel flash-sheet

4. Launch the application:

   .. code-block:: bash

       flash-sheet

Platform-Specific Instructions
------------------------------

Windows Installation
~~~~~~~~~~~~~~~~~~~~

**Prerequisites:**

- Windows 10 or later
- Administrator privileges for installation

**Installation Steps:**

1. Download the installer from the releases page
2. Right-click the installer and select "Run as administrator"
3. Follow the installation wizard:

   - Choose installation directory (default: C:\Program Files\Flash Sheet)
   - Select components to install
   - Create desktop shortcut (recommended)

4. The installer will add Flash Sheet to your PATH

**Uninstallation:**

- Use Windows Settings → Apps → Flash Sheet → Uninstall
- Or run the uninstaller from the installation directory

macOS Installation
~~~~~~~~~~~~~~~~~~

**Prerequisites:**

- macOS 10.15 or later
- Gatekeeper may need to be configured for unsigned applications

**Installation Steps:**

1. Download the .dmg file from the releases page
2. Double-click the .dmg file to mount it
3. Drag Flash Sheet to the Applications folder
4. Eject the disk image

**First Launch:**

macOS may show a security warning. To allow Flash Sheet to run:

1. Go to System Preferences → Security & Privacy
2. Click the "Allow" button next to Flash Sheet
3. Launch Flash Sheet from Applications

**Uninstallation:**

- Drag Flash Sheet from Applications to Trash
- Empty the Trash

Linux Installation
~~~~~~~~~~~~~~~~~~

**Ubuntu/Debian:**

1. Download the .deb package from the releases page
2. Install using dpkg:

   .. code-block:: bash

       sudo dpkg -i flash-sheet.deb
       sudo apt-get install -f  # Fix any dependencies

3. Launch from applications menu or command line:

   .. code-block:: bash

       flash-sheet

**Fedora/CentOS:**

1. Download the .rpm package from the releases page
2. Install using rpm:

   .. code-block:: bash

       sudo rpm -i flash-sheet.rpm

3. Launch the application

**AppImage (Universal):**

1. Download the AppImage file
2. Make it executable and run:

   .. code-block:: bash

       chmod +x flash-sheet.AppImage
       ./flash-sheet.AppImage

**Uninstallation:**

- For packaged installations: Use your package manager
- For AppImage: Simply delete the file

Post-Installation Setup
-----------------------

First Run Configuration
~~~~~~~~~~~~~~~~~~~~~~~

1. **Language Selection**: Choose your preferred language
2. **Theme Selection**: Choose light or dark theme
3. **Default Settings**: Configure default data loading options
4. **File Associations**: Associate file types with Flash Sheet (optional)

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

**Memory Settings:**

- Default memory allocation is automatic
- For large datasets, increase available memory in settings
- Close other applications when working with big data

**Display Settings:**

- Use high DPI scaling for high-resolution displays
- Adjust font sizes for readability
- Enable hardware acceleration if available

Data Directory Setup
~~~~~~~~~~~~~~~~~~~~

**Default Data Locations:**

- **Windows**: ``%APPDATA%\Flash Sheet``
- **macOS**: ``~/Library/Application Support/Flash Sheet``
- **Linux**: ``~/.config/flash-sheet``

**Custom Data Directory:**

1. Create a dedicated folder for your data
2. In Flash Sheet settings, set the default data directory
3. Place templates and configuration files there

Troubleshooting Installation
----------------------------

Common Installation Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~

**"Python not found" Error:**

- Install Python 3.7+ from python.org
- Add Python to your system PATH
- Restart your command prompt/terminal

**Permission Denied:**

- Run installer as administrator (Windows)
- Use sudo for system-wide installation (Linux/macOS)
- Check folder permissions

**Missing Dependencies:**

- Install required system packages
- Update pip: ``pip install --upgrade pip``
- Use virtual environment to avoid conflicts

**Qt/PySide6 Issues:**

- Install Qt development libraries
- Update graphics drivers
- Check display server configuration (Linux)

**Antivirus Blocking:**

- Add Flash Sheet to antivirus exclusions
- Disable real-time scanning during installation
- Download from official sources only

Verification and Testing
~~~~~~~~~~~~~~~~~~~~~~~~

**Installation Verification:**

1. Launch Flash Sheet
2. Check version in Help → About
3. Load a sample CSV file
4. Try basic export functionality

**Performance Testing:**

1. Load a sample dataset
2. Test different view modes
3. Try export operations
4. Monitor memory usage

Uninstallation
--------------

Complete Removal
~~~~~~~~~~~~~~~~

**Windows:**

1. Go to Settings → Apps → Flash Sheet
2. Click "Uninstall"
3. Remove user data if desired:

   .. code-block:: batch

       rmdir /s "%APPDATA%\Flash Sheet"

**macOS:**

1. Drag Flash Sheet from Applications to Trash
2. Remove user data:

   .. code-block:: bash

       rm -rf ~/Library/Application\ Support/Flash\ Sheet

**Linux:**

1. Use your package manager to uninstall
2. Remove user data:

   .. code-block:: bash

       rm -rf ~/.config/flash-sheet

Updating Flash Sheet
--------------------

Automatic Updates
~~~~~~~~~~~~~~~~~

Flash Sheet can check for updates automatically:

1. Go to Help → Check for Updates
2. Download and install available updates
3. Restart the application

Manual Updates
~~~~~~~~~~~~~~

1. Download the new version from the releases page
2. Close Flash Sheet
3. Run the installer for the new version
4. The installer will update your existing installation

**From Source:**

.. code-block:: bash

    cd flash-sheet
    git pull origin main
    pip install -r requirements.txt
    python main.py

Backup Before Updating
~~~~~~~~~~~~~~~~~~~~~~

- Export important data
- Backup configuration files
- Note custom settings
- Save project files

Command Line Usage
------------------

Advanced Installation Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Silent Installation (Windows):**

.. code-block:: batch

    flash-sheet-setup.exe /S /D=C:\Program Files\Flash Sheet

**Custom Installation Directory:**

.. code-block:: bash

    # Linux/macOS
    export FLASH_SHEET_HOME=/opt/flash-sheet
    pip install --target=$FLASH_SHEET_HOME flash-sheet

**Development Installation:**

.. code-block:: bash

    pip install -e .  # Editable installation for development

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

**Configuration via Environment:**

.. code-block:: bash

    export FLASH_SHEET_CONFIG_DIR=~/.flash-sheet
    export FLASH_SHEET_LOG_LEVEL=DEBUG
    export FLASH_SHEET_MAX_MEMORY=4GB

**Python Path Configuration:**

.. code-block:: bash

    export PYTHONPATH=$PYTHONPATH:/path/to/flash-sheet

Network Installation
--------------------

Enterprise Deployment
~~~~~~~~~~~~~~~~~~~~~

**Windows Group Policy:**

1. Create a software distribution point
2. Use MSI installer for group policy deployment
3. Configure installation settings via GPO

**Linux Package Management:**

1. Create internal package repository
2. Distribute .deb/.rpm packages
3. Use configuration management tools (Ansible, Puppet)

**macOS MDM:**

1. Use mobile device management solutions
2. Deploy via MDM profile
3. Configure security policies

Offline Installation
~~~~~~~~~~~~~~~~~~~~

**Air-Gapped Systems:**

1. Download all dependencies on connected system
2. Transfer files to offline system
3. Install using local package cache:

   .. code-block:: bash

       pip install --no-index --find-links=/path/to/packages flash-sheet

Getting Help
------------

Installation Support
~~~~~~~~~~~~~~~~~~~~

- **Documentation**: Check troubleshooting section
- **Issue Tracker**: Report installation problems
- **Community Forum**: Ask installation questions
- **Email Support**: contact@flash-sheet.org

System Compatibility
~~~~~~~~~~~~~~~~~~~~

**Tested Platforms:**

- Windows 10, 11
- macOS 10.15 - 12.x
- Ubuntu 18.04 - 22.04
- CentOS 7, 8
- Fedora 34+

**Known Limitations:**

- ARM processors: Limited support
- Wayland (Linux): May require X11 fallback
- Older graphics drivers: May need updates

Next Steps
----------

After successful installation:

1. :doc:`../user_guide/getting_started` - Learn the basics
2. :doc:`../user_guide/basic_usage` - Start using Flash Sheet
3. :doc:`../user_guide/advanced_features` - Explore advanced features
4. :doc:`../developer_guide/development_guide` - For developers