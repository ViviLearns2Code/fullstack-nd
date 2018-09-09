# ToLearn
This app was created as part of the Udacity Full-Stack Nanodegree (Item Catalog project).

## Prerequisites
To run this app, you need to have Oracle VM VirtualBox 5.1.26 and Vagrant 1.9.7 installed on your machine. Furthermore, you need to clone the Udacity [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm) repository. You need to add the following line to that repository's `Vagrantfile`:

`pip3 install --upgrade google-api-python-client`

This line will install the additional python library needed for the app's authorization process.

Clone the ItemCatalog repository into the `vagrant` subfolder of the Udacity repository. After that, prepare to launch the app:

* `cd` to the `vagrant` subfolder
* boot the virtual machine by running `vagrant up` and login with `vagrant ssh`
* `cd` to the `itemcatalog` subfolder
* Enter `python3 database_setup.py` to create an empty database

After performing these steps, you will be able to launch the application with `python3 application.py`. You can access the app via `http://localhost:8080`. It is recommended to use either Chrome or Firefox for this app because these browsers support the needed ES6 features.

## Run the App
* Login with your Google credentials (a new user will be created for you if you don't already have one)
* On the category page, you can create your own learning categories, rename them and delete them
* You can navigate to a learning category's item page and create/delete learning items that belong to the learning category
* You can also edit the learning items
![Alt category page](https://raw.githubusercontent.com/ViviLearns2Code/ItemCatalog/master/docs/category.jpg)
![Alt item page](https://raw.githubusercontent.com/ViviLearns2Code/ItemCatalog/master/docs/item.jpg)
![Alt create/update item](https://raw.githubusercontent.com/ViviLearns2Code/ItemCatalog/master/docs/item_form.jpg)
You can modify the `populate_db.py` file and run it to pre-populate the database with example data.

## API
The app offers three JSON endpoints. Before you use an endpoint to request data, you need to get an API token from the app. A token expires after 3600 seconds. See `docs/test_api.html` for an example of how requests can be carried out with the token (not part of the app, just an example file).