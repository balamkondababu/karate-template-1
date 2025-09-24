Feature: User Management

Background:
  * url 'https://api.sample.com'
  * configure headers = { Accept: 'application/json', Content-Type: 'application/json' }
  * def testData = { validUserId: 1, validUserName: 'John Doe' }

Scenario: Get list of users - returns 200
  Given path '/users'
  When method get
  Then status 200
  And match response == '#[]'

Scenario: Get list of users - empty list
  Given path '/users'
  When method get
  Then status 200
  And match response == '[]'

Scenario: Get user by ID - returns 200
  Given path '/users/1'
  When method get
  Then status 200
  And match response contains { id: '#number', name: '#string' }

Scenario: Get user by ID - invalid ID
  Given path '/users/abc'
  When method get
  Then status 400
  And match response contains { error: '#string' }

Scenario: Get user by ID - user not found
  Given path '/users/999'
  When method get
  Then status 404
  And match response contains { error: '#string' }

Scenario Outline: Get list of users with query parameters
  Given path '/users'
  And param limit = <limit>
  And param offset = <offset>
  When method get
  Then status 200
  And match response == '#[]'
  Examples:
    | limit | offset |
    | 10    | 0      |
    | 20    | 10     |
    | 50    | 20     |

Feature: User Retrieval

Background:
  * url 'https://api.sample.com'
  * configure headers = { Accept: 'application/json', Content-Type: 'application/json' }
  * def testData = { validUserId: 1, validUserName: 'John Doe' }

Scenario: Get user by ID - returns 200
  Given path '/users/1'
  When method get
  Then status 200
  And match response contains { id: '#number', name: '#string' }

Scenario: Get user by ID - invalid ID
  Given path '/users/abc'
  When method get
  Then status 400
  And match response contains { error: '#string' }

Scenario: Get user by ID - user not found
  Given path '/users/999'
  When method get
  Then status 404
  And match response contains { error: '#string' }

Feature: Error Handling

Background:
  * url 'https://api.sample.com'
  * configure headers = { Accept: 'application/json', Content-Type: 'application/json' }
  * def testData = { validUserId: 1, validUserName: 'John Doe' }

Scenario: Get user by ID - invalid ID
  Given path '/users/abc'
  When method get
  Then status 400
  And match response contains { error: '#string' }

Scenario: Get user by ID - user not found
  Given path '/users/999'
  When method get
  Then status 404
  And match response contains { error: '#string' }

To update the existing karate-config.js, add the following test data variables:
```javascript
testData: {
  validUserId: 1,
  validUserName: 'John Doe'
}
```