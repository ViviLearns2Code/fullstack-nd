# Logs Analysis
This python tool extracts, aggregates and sorts data from three database tables. The database contains three tables which record website articles, their authors and a view log for the articles. The python tool answers three questions:
* Which are the three most popular articles
* How popular are the involved authors
* Which day(s) had more than 1% failed requests

The tool performs three SQL statements and then prints out the results as a plain text list.

## Download
You need to have Oracle VM VirtualBox 5.1.26 and Vagrant 1.9.7 installed on your machine. Furthermore, you need to clone the Udacity [ fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm) repository and download the `newsdata.sql` file from Udacity.

To log in to the virtual machine, `cd` to the `vagrant` subfolder. Run `vagrant up` and once the virtual machine has booted, `vagrant ssh`.

To use the tool, clone this repository into the `vagrant` subfolder of the `fullstack-nanodegree-vm` folder. Copy the `newsdata.sql` file into the same directory. To load the data into the database, run `psql -d news -f newsdata.sql`. Once this is complete, run `python newsdb.py`. The output will be identical to the text in `output_plaintext.txt`.
