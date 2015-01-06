# End to End Testing of Angular Apps

## Pre-requisites:

1. Install [Protractor](http://angular.github.io/protractor/#/tutorial)
2. Read the documenation above!!!
3. Git your local development env (Fig) up and running before running any test
4. Some of the the tests (i.e. admissions), require that you have multi-tenant set up on your local machine, see the notes [here](https://github.com/bufke/bsc-ops/blob/master/django-sis/development.md) about getting multi-tenant supported on your local machine. 

## Running a test:

1. Navigage to the `static_files/app/tests` dir
2. Start webDriver server: 

    `webdriver-manager start`

3. Run the tests with protractor: 

    `protractor conf.js`
    
4. Optionally run a particular test suite: 

    `protractor conf.js --suite admissions`

## `conf.js`

`rootElement` : This will probably be deprecated soon, pending a re-write of the angular app. For pages without a "ng-view" you have to specify a root element