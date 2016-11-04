# proj6-mongo
Simple list of dated memos kept in MongoDB database

##Configuration 

A simple Flask app that displays all the dated memos it finds in a MongoDB database.

- secrets/admin_secrets.py holds configuration information for MongoDB
  database, including the administrative password.  
- secrets/client_secrets.py holds configuration information for  application. 

## Author 
version by  YaoCheng Gao

## Status

The user be able to add dated memos, either from the same index page or from a separate page. 
Memos be displayed in date order. 
The user be able to delete memos. 

## To run automated tests 
* `nosetests`
## To Install and Run
    bash ./configure

    run create_db.py to create user and db before test and app 

    make test    # make all test, should pass 
    make service # service run background

