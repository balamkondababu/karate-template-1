Feature: User Management

Background:
  * url 'https://example.com'
  * configure headers = { Content-Type: 'application/json' }
  * def testData = { name: 'John Doe' }

Scenario: Get list of users
  Given path '/users'
  When method GET
  Then status 200
  And match response == '#[]'

Scenario: Get list of users with invalid request
  Given path '/users'
  And header Content-Type = 'text/plain'
  When method GET
  Then status 415

Scenario: Create a new user with valid data
  Given path '/users'
  And request { name: '#(testData.name)' }
  When method POST
  Then status 201
  And match response contains { id: '#number', name: '#string' }

Scenario: Create a new user with missing name
  Given path '/users'
  And request {}
  When method POST
  Then status 400

Scenario: Create a new user with invalid name
  Given path '/users'
  And request { name: 123 }
  When method POST
  Then status 400

Scenario: Get user by ID with valid ID
  Given path '/users/1'
  When method GET
  Then status 200
  And match response contains { id: '#number', name: '#string' }

Scenario: Get user by ID with invalid ID
  Given path '/users/abc'
  When method GET
  Then status 400

Scenario: Get user by ID with non-existent ID
  Given path '/users/999'
  When method GET
  Then status 404

Scenario Outline: Get user by ID with different IDs
  Given path '/users/<id>'
  When method GET
  Then status <status>
  And match response == <response>

  Examples:
    | id | status | response         |
    | 1  | 200    | { id: 1, name: 'John Doe' } |
    | 2  | 200    | { id: 2, name: 'Jane Doe' } |
    | 3  | 404    | { error: 'User not found' } |

Feature: User Retrieval by Application ID

Background:
  * url 'https://example.com'
  * configure headers = { Content-Type: 'application/json' }
  * def testData = { id: 1, applicationId: 1 }

Scenario: Get user by application ID with valid IDs
  Given path '/users/1/1'
  When method GET
  Then status 200
  And match response contains { id: '#number', name: '#string' }

Scenario: Get user by application ID with invalid IDs
  Given path '/users/abc/1'
  When method GET
  Then status 400

Scenario: Get user by application ID with non-existent IDs
  Given path '/users/1/999'
  When method GET
  Then status 404

Scenario Outline: Get user by application ID with different IDs
  Given path '/users/<id>/<applicationId>'
  When method GET
  Then status <status>
  And match response == <response>

  Examples:
    | id | applicationId | status | response         |
    | 1  | 1             | 200    | { id: 1, name: 'John Doe' } |
    | 2  | 2             | 200    | { id: 2, name: 'Jane Doe' } |
    | 3  | 3             | 404    | { error: 'User not found' } |