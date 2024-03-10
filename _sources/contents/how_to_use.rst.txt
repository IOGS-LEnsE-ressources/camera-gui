How to use these ressources ?
#############################

You're actually on the *GitHup Page* of the `Camera GUI Git Repository <https://github.com/IOGS-LEnsE-ressources/camera-gui/>`_.

This repository gathers **ressources** to setup industrial cameras (Basler, IDS...) and to collect images in **Python applications** (console or :abbr:`GUI (graphical user interface)` applications).

.. figure:: ../_static/images/pieces_machine_vision.png
	:width: 50%
	:align: center
	
	Example of machine vision image. `Machine Vision platform from the LEnsE <https://iogs-lense-platforms.github.io/machine-vision/index.html>`_

|

This repository contains :

* the **source codes** of the different wrappers in the :file:`progs/brandname/src/` directory (where brandname is the name of the camera manufacturer). 	
* **usage examples** in the :file:`progs/brandname/examples/` directory 
* the **documentation** in the :file:`docs/` directory (developed with `Sphinx <https://www.sphinx-doc.org/>`_)


GitHub repositories
*******************

There are different ways to get a copy of a repository's files on **GitHub**. You can:

* **Download** a snapshot of a repository's files as a **zip file** to your own (local) computer.
	* To simply use the content of the repository
* **Clone** a repository to your local computer using *Git*.
	* To use *Git* to track and manage your changes, to sync your locally-made changes with the GitHub-hosted repository
* **Fork** a repository to create a new repository on GitHub.
	* to use the original repository's data as a basis for your own project on GitHub - Advanced use of *Git*, not documented in this section.
* **Browse** the repository's directories and download only specific files.

From the GitHub Documentation : `Downloading files from GitHub <https://docs.github.com/en/get-started/start-your-journey/downloading-files-from-github>`_.


Download the repository
=======================

This is the **easiest way** to obtain the most **up-to-date source code**. 

To download a repository, you need to follow these steps:

#. Navigate to the main page of the repository you want to clone.
#. Above the list of files, click :menuselection:`<> Code`.

	.. figure:: ../_static/images/how_to/git_hub_code_icon.png
		:align: center
		:width: 50%

#. Click :menuselection:`Download ZIP`

	.. figure:: ../_static/images/how_to/git_hub_download.png
		:align: center
		:width: 80%

#. Change the current working directory to the location where you want to download the repository ZIP file.
#. Go into your file browser and go to the selected directory for this repository.
#. Unzip the archive file.


Clone the repository
====================

This is the **best way** to obtain the most **up-to-date source code**. However, you need to be familiar with the use of **Git** and a client software able to manage git repository must be installed (such as :program:`Git Bash` or :program:`GitHub Desktop`...).


To clone a repository, you need to follow these steps:

#. Navigate to the main page of the repository you want to clone.
#. Above the list of files, click :menuselection:`<> Code`.

	.. figure:: ../_static/images/how_to/git_hub_code_icon.png
		:align: center
		:width: 50%
		
#. Copy the URL for the repository in the corresponding HTTPS `Clone` sub-section.


	.. figure:: ../_static/images/how_to/git_hub_https_clone.png
		:align: center
		:width: 80%

#. Open :program:`Git Bash` (or another git management software).
#. Change the current working directory to the location where you want the cloned directory.
#. Type :command:`git clone`, and then paste the URL you copied earlier.

	.. code::
	
		git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY

#. Press :kbd:`Enter` to create your local clone.
#. Go into your file browser and go to the selected directory for this repository.

From the GitHub Documentation : `Cloning a repository <https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository>`_.


Download specific files
=======================

The most **boring way** to obtain files in a GitHub repository is to browse in the different directories and to manually download each file you need.


To download specific files from a repository, you need to follow these steps:

#. Navigate to the main page of the repository you want to clone.
#. Browse through the different directories.

	.. figure:: ../_static/images/how_to/git_hub_browse.png
		:align: center
		:width: 80%

#. Open a file and click :menuselection:`Download raw file` icon.

	.. figure:: ../_static/images/how_to/git_hub_raw_download.png
		:align: center
		:width: 80%

#. Change the current working directory to the location where you want to download the raw file.