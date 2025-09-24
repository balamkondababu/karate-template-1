### karate-config.js Updates
Add the following test data variables to the existing configuration:
```javascript
testData: {
  validUserName: 'John Doe',
  validUserId: 1,
  invalidUserId: 999,
  validApplicationId: 1,
  invalidApplicationId: 999
}
```

### Feature Files

#### user-management.feature
```gherkin
Feature: User Management

Background:
  * url baseUrl
  * configure headers = { 'Content-Type': 'application/json' }
  * def testData = { 
    validUserName: '#(testData.validUserName)',
    validUserId: '#(testData.validUserId)',
    invalidUserId: '#(testData.invalidUserId)',
    validApplicationId: '#(testData.validApplicationId)',
    invalidApplicationId: '#(testData.invalidApplicationId)'
  }

Scenario: Get list of users
  Given path 'users'
  When method get
  Then status 200
  And match response == '#[]'

Scenario: Create a new user
  Given path 'users'
  And request { name: '#(testData.validUserName)' }
  When method post
  Then status 201
  And match response contains { id: '#number', name: '#string' }

Scenario: Get user by ID - valid ID
  Given path 'users/' + testData.validUserId
  When method get
  Then status 200
  And match response contains { id: '#number', name: '#string' }

Scenario: Get user by ID - invalid ID
  Given path 'users/' + testData.invalidUserId
  When method get
  Then status 404

Scenario: Get user by application ID - valid IDs
  Given path 'users/' + testData.validUserId + '/' + testData.validApplicationId
  When method get
  Then status 200
  And match response contains { id: '#number', name: '#string' }

Scenario: Get user by application ID - invalid IDs
  Given path 'users/' + testData.invalidUserId + '/' + testData.invalidApplicationId
  When method get
  Then status 404

Scenario Outline: Create user with different names
  Given path 'users'
  And request { name: '<name>' }
  When method post
  Then status 201
  And match response contains { id: '#number', name: '<name>' }
Examples:
  | name      |
  | John Doe  |
  | Jane Doe  |
  | Foo Bar   |

Scenario: Create user with missing name
  Given path 'users'
  And request {}
  When method post
  Then status 400

Scenario: Create user with invalid name
  Given path 'users'
  And request { name: 123 }
  When method post
  Then status 400
```

#### error-handling.feature
```gherkin
Feature: Error Handling

Background:
  * url baseUrl
  * configure headers = { 'Content-Type': 'application/json' }

Scenario: Get user by ID - invalid ID
  Given path 'users/999'
  When method get
  Then status 404

Scenario: Create user with missing name
  Given path 'users'
  And request {}
  When method post
  Then status 400

Scenario: Create user with invalid name
  Given path 'users'
  And request { name: 123 }
  When method post
  Then status 400
```

Note: The above feature files cover the provided endpoints and scenarios. You can add more scenarios and test cases as needed. Also, make sure to update the `baseUrl` and `commonHeaders` in the `karate-config.js` file accordingly.