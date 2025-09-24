Feature: User Management

Background:
  * url baseUrl
  * configure headers = { 'Content-Type': 'application/json' }
  * def testData = { 
    "validUserName": "John Doe",
    "validUserId": 1,
    "invalidUserId": 99999
  }

Scenario: Get list of users
  Given path 'users'
  When method get
  Then status 200
  And match response == '#[]'

Scenario: Get list of users with invalid request
  Given path 'users'
  And header Accept = 'application/xml'
  When method get
  Then status 406

Scenario: Create a new user with valid data
  Given path 'users'
  And request { name: '#(testData.validUserName)' }
  When method post
  Then status 201
  And match response == { id: '#number', name: '#string' }

Scenario: Create a new user with invalid data
  Given path 'users'
  And request { }
  When method post
  Then status 400

Scenario: Get user by ID with valid ID
  Given path 'users/' + testData.validUserId
  When method get
  Then status 200
  And match response == { id: '#number', name: '#string' }

Scenario: Get user by ID with invalid ID
  Given path 'users/' + testData.invalidUserId
  When method get
  Then status 404

Scenario Outline: Get user by ID with different IDs
  Given path 'users/' + <id>
  When method get
  Then status <status>
  And match response == <response>

  Examples:
    | id | status | response          |
    | 1  | 200    | { id: 1, name: '#string' } |
    | 99999 | 404 | { error: '#string' } |

Feature: User Application Management

Background:
  * url baseUrl
  * configure headers = { 'Content-Type': 'application/json' }
  * def testData = { 
    "validApplicationId": 1,
    "invalidApplicationId": 99999
  }

Scenario: Get user by application ID with valid IDs
  Given path 'users/' + testData.validUserId + '/' + testData.validApplicationId
  When method get
  Then status 200
  And match response == { id: '#number', name: '#string' }

Scenario: Get user by application ID with invalid IDs
  Given path 'users/' + testData.invalidUserId + '/' + testData.invalidApplicationId
  When method get
  Then status 404

Scenario Outline: Get user by application ID with different IDs
  Given path 'users/' + <userId> + '/' + <applicationId>
  When method get
  Then status <status>
  And match response == <response>

  Examples:
    | userId | applicationId | status | response          |
    | 1      | 1             | 200    | { id: 1, name: '#string' } |
    | 99999  | 99999         | 404    | { error: '#string' } | 

To be added to karate-config.js:
```javascript
testData: {
  validUserName: 'John Doe',
  validUserId: 1,
  invalidUserId: 99999,
  validApplicationId: 1,
  invalidApplicationId: 99999
}
```