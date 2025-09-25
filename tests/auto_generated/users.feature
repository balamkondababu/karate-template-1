Feature: User Management

Background:
  * url 'https://example.com'
  * configure headers = { Content-Type: 'application/json' }
  * def testData = { name: 'John Doe' }

Scenario: Get list of users - returns 200
  Given path '/users'
  When method get
  Then status 200
  And match response == '#array'
  And match each response[] contains { id: '#number', name: '#string' }

Scenario: Get list of users - invalid request
  Given path '/users'
  And header Content-Type = 'text/plain'
  When method get
  Then status 415

Scenario: Get user by ID - returns 200
  Given path '/users/1'
  When method get
  Then status 200
  And match response == { id: '#number', name: '#string' }

Scenario: Get user by ID - invalid ID
  Given path '/users/abc'
  When method get
  Then status 400

Scenario: Get user by ID - user not found
  Given path '/users/999'
  When method get
  Then status 404

Scenario: Get user by ID - returns 200 with valid application ID
  Given path '/users/1/1'
  When method get
  Then status 200
  And match response == { id: '#number', name: '#string' }

Scenario: Get user by ID - returns 400 with invalid application ID
  Given path '/users/1/abc'
  When method get
  Then status 400

Scenario Outline: Get list of users with query parameters
  Given path '/users'
  And param limit = '<limit>'
  And param offset = '<offset>'
  When method get
  Then status 200
  And match response == '#array'
  And match each response[] contains { id: '#number', name: '#string' }

  Examples:
    | limit | offset |
    | 10    | 0     |
    | 20    | 10    |
    | 50    | 20    |

Scenario Outline: Create a new user with valid data
  Given path '/users'
  And request { name: '<name>' }
  When method post
  Then status 201
  And match response == { id: '#number', name: '<name>' }

  Examples:
    | name      |
    | John Doe  |
    | Jane Doe  |

Scenario Outline: Create a new user with invalid data
  Given path '/users'
  And request { name: '<name>' }
  When method post
  Then status 400

  Examples:
    | name      |
    |           |
    | <null>    |

Scenario: Create a new user with missing required parameters
  Given path '/users'
  And request {}
  When method post
  Then status 400

Scenario: Create a new user with invalid data type
  Given path '/users'
  And request { name: 123 }
  When method post
  Then status 400

Scenario: Get user by ID with authentication
  Given path '/users/1'
  And header Authorization = 'Bearer token'
  When method get
  Then status 200
  And match response == { id: '#number', name: '#string' }

Scenario: Get user by ID without authentication
  Given path '/users/1'
  When method get
  Then status 401

Scenario: Get user by ID with invalid authentication
  Given path '/users/1'
  And header Authorization = 'Bearer invalid-token'
  When method get
  Then status 401